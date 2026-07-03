#!/usr/bin/env bash
# MEDISTOCK - Setup script para EC2 Ubuntu 22.04 LTS
# Ejecutar desde el directorio raiz del proyecto (donde estan backend_django/, frontend_vite/, etc.)
#
# Uso:
#   sudo bash deploy/setup.sh
#
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_NAME="medistock"
DB_USER="medistock"
DB_PASS="medistock123"  # CAMBIAR EN PRODUCCION

echo "============================================="
echo "  MEDISTOCK - Setup automatizado para AWS EC2"
echo "============================================="
echo "Directorio del proyecto: $PROJECT_DIR"
echo ""

# Requiere sudo
if [ "$EUID" -ne 0 ]; then
  echo "Este script debe ejecutarse con sudo."
  exit 1
fi

# 1. Actualizar paquetes
echo "[1/8] Actualizando paquetes..."
apt-get update -qq
apt-get upgrade -y -qq

# 2. Instalar dependencias del sistema
echo "[2/8] Instalando Python, Node, PostgreSQL, Nginx..."
apt-get install -y -qq \
  python3 python3-pip python3-venv \
  postgresql postgresql-contrib \
  nginx \
  curl git build-essential \
  ca-certificates gnupg

# Node 20 LTS
echo "[3/8] Instalando Node.js 20 LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y -qq nodejs

# 3. Configurar PostgreSQL
echo "[4/8] Configurando PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql <<EOF
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
  END IF;
END \$\$;
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# 4. Backend: virtualenv + deps
echo "[5/8] Instalando backend (Django)..."
cd "$PROJECT_DIR/backend_django"
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

if [ ! -f .env ]; then
  cp .env.example .env
  # Generar SECRET_KEY aleatoria
  SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
  sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET|" .env
  sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASS|" .env
  echo "  Archivo .env creado. EDITA $PROJECT_DIR/backend_django/.env para configurar MercadoPago."
fi

# Migraciones + seed inicial de la BD
./venv/bin/python manage.py migrate
./venv/bin/python manage.py seed_demo
./venv/bin/python manage.py collectstatic --noinput

# 5. Frontend principal
echo "[6/8] Build del frontend principal..."
cd "$PROJECT_DIR/frontend_vite"
if [ ! -f .env ]; then
  echo "VITE_API_URL=http://$(curl -s ifconfig.me)" > .env
fi
npm ci
npm run build

# 6. Sitio Cruz Amarilla
echo "[7/8] Build del sitio Cruz Amarilla..."
cd "$PROJECT_DIR/consumidor-externo"
if [ ! -f .env.local ]; then
  echo "NEXT_PUBLIC_MEDISTOCK_API=http://$(curl -s ifconfig.me)" > .env.local
fi
npm ci
npm run build

# 7. Servicios systemd + Nginx
echo "[8/8] Configurando servicios systemd y Nginx..."
PROJECT_DIR_ESCAPED=$(echo "$PROJECT_DIR" | sed 's|/|\\/|g')
sed "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" "$PROJECT_DIR/deploy/systemd/medistock-backend.service" \
  > /etc/systemd/system/medistock-backend.service
sed "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" "$PROJECT_DIR/deploy/systemd/medistock-frontend.service" \
  > /etc/systemd/system/medistock-frontend.service
sed "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" "$PROJECT_DIR/deploy/systemd/cruz-amarilla.service" \
  > /etc/systemd/system/cruz-amarilla.service

cp "$PROJECT_DIR/deploy/nginx.conf" /etc/nginx/sites-available/medistock
ln -sf /etc/nginx/sites-available/medistock /etc/nginx/sites-enabled/medistock
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable medistock-backend medistock-frontend cruz-amarilla
systemctl restart medistock-backend medistock-frontend cruz-amarilla
nginx -t && systemctl restart nginx

# Firewall
ufw allow OpenSSH 2>/dev/null || true
ufw allow 'Nginx Full' 2>/dev/null || true
echo "y" | ufw enable 2>/dev/null || true

PUBLIC_IP=$(curl -s ifconfig.me)
echo ""
echo "============================================="
echo "  Deploy completado exitosamente"
echo "============================================="
echo ""
echo "URLs publicas:"
echo "  MEDISTOCK (principal):  http://$PUBLIC_IP"
echo "  Cruz Amarilla (externo): http://$PUBLIC_IP/cruz-amarilla"
echo "  Django admin:            http://$PUBLIC_IP/admin"
echo ""
echo "Servicios:"
echo "  sudo systemctl status medistock-backend"
echo "  sudo systemctl status medistock-frontend"
echo "  sudo systemctl status cruz-amarilla"
echo ""
echo "Logs:"
echo "  sudo journalctl -u medistock-backend -f"
echo ""
echo "IMPORTANTE: Edita $PROJECT_DIR/backend_django/.env y agrega tus credenciales de MercadoPago."
echo "Luego: sudo systemctl restart medistock-backend"
