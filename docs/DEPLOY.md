# Guía de deploy en AWS EC2

Guía paso a paso para levantar MEDISTOCK en una instancia EC2 de AWS, desde cero. Asume que el lector nunca ha usado AWS.

---

## Paso 1: Crear cuenta AWS

1. Ir a **https://aws.amazon.com** y click en "Crear cuenta gratuita".
2. Si tu profe te entregó una cuenta de AWS Academy / Learner Lab, usa esa.
3. Una vez dentro de la consola, asegúrate de estar en la región **us-east-1 (N. Virginia)** o **sa-east-1 (São Paulo)** — abajo a la derecha de la consola.

---

## Paso 2: Lanzar instancia EC2

1. En la consola AWS, busca "EC2" en la barra superior y entra al servicio.
2. Click en **"Launch instance"** (Lanzar instancia).
3. Configuración:
   - **Name**: `medistock-prod`
   - **AMI**: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type. **Importante**: que diga "Free tier eligible".
   - **Instance type**: `t2.micro` (Free tier eligible).
   - **Key pair**: Click "Create new key pair". Nombre: `medistock-key`. Tipo: RSA · .pem. Click "Create key pair" — se descarga el archivo `.pem`. **GUÁRDALO bien, no se puede volver a descargar.**
   - **Network settings**: Click "Edit" y asegúrate que estén marcados:
     - ✅ Allow SSH traffic from: Anywhere (0.0.0.0/0)
     - ✅ Allow HTTP traffic from the internet
     - ✅ Allow HTTPS traffic from the internet
   - **Configure storage**: 20 GB gp3 (gratis hasta 30GB).
4. Click **"Launch instance"**.
5. Espera 1-2 minutos. Cuando el estado sea "Running" y el "Status check" sea "2/2 checks passed", está lista.

---

## Paso 3: Conectarte por SSH

En tu computador, abre terminal:

```bash
# Linux / Mac
chmod 400 ~/Downloads/medistock-key.pem
ssh -i ~/Downloads/medistock-key.pem ubuntu@TU-IP-PUBLICA

# Windows (PowerShell)
ssh -i C:\Users\TU_USUARIO\Downloads\medistock-key.pem ubuntu@TU-IP-PUBLICA
```

La **IP pública** la encuentras en la consola EC2 → selecciona tu instancia → pestaña "Details" → "Public IPv4 address".

La primera vez te preguntará si confías en el host. Escribe `yes`.

Si todo va bien, ves un prompt: `ubuntu@ip-172-...:~$`

---

## Paso 4: Subir el código a la instancia

Tienes dos opciones:

### Opción A — Via Git (recomendado si el código está en GitHub)

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/TU-USUARIO/medistock.git
cd medistock
```

### Opción B — Via SCP desde tu computador

Desde tu computador local (NO desde la EC2), corre:

```bash
# Comprime el proyecto
cd ruta/al/proyecto
zip -r medistock.zip medistock/ -x "**/node_modules/*" "**/venv/*" "**/.next/*"

# Sube a la instancia
scp -i ~/Downloads/medistock-key.pem medistock.zip ubuntu@TU-IP:~/

# Conectate y descomprime
ssh -i ~/Downloads/medistock-key.pem ubuntu@TU-IP
unzip medistock.zip
cd medistock
```

---

## Paso 5: Ejecutar el setup automatizado

Una vez dentro del directorio `medistock` en la instancia:

```bash
sudo bash deploy/setup.sh
```

El script hace **todo** automáticamente:
- Instala Python, Node.js 20, PostgreSQL, Nginx.
- Crea la base de datos `medistock`.
- Instala dependencias de backend y frontend.
- Ejecuta el seed (carga productos demo y usuarios).
- Hace build de ambos frontends.
- Configura services de systemd (auto-arranque).
- Configura Nginx como reverse proxy.
- Abre puertos en el firewall.

**Tiempo estimado: 5-10 minutos.**

Al final imprime:
```
URLs publicas:
  MEDISTOCK (principal):  http://TU-IP
  Cruz Amarilla (externo): http://TU-IP/cruz-amarilla
  API Docs (Swagger):      http://TU-IP/docs
```

---

## Paso 6: Configurar MercadoPago

Edita el `.env` del backend:

```bash
nano /home/ubuntu/medistock/backend/.env
```

Reemplaza:
```
MERCADOPAGO_ACCESS_TOKEN=TEST-TU-TOKEN-AQUI
MERCADOPAGO_PUBLIC_KEY=TEST-TU-PUBLIC-KEY-AQUI
```

Por las credenciales reales obtenidas en [MercadoPago Developers](https://www.mercadopago.cl/developers/panel/app). Ver guía en `docs/MERCADOPAGO_SETUP.md`.

También actualiza:
```
FRONTEND_URL=http://TU-IP
BACKEND_URL=http://TU-IP
```

Guardar (Ctrl+O, Enter, Ctrl+X) y reiniciar el backend:

```bash
sudo systemctl restart medistock-backend
```

---

## Paso 7: Verificar

Abre en tu navegador:

- **http://TU-IP** → Landing de MEDISTOCK
- **http://TU-IP/catalogo** → Catálogo
- **http://TU-IP/cruz-amarilla** → Farmacia Cruz Amarilla
- **http://TU-IP/docs** → Swagger UI de la API

Prueba con cualquier cuenta demo:
- `admin@medistock.cl` / `admin123` → Panel admin
- `paciente@gmail.com` / `paciente123` → Cliente

---

## Comandos útiles

### Ver estado de servicios

```bash
sudo systemctl status medistock-backend
sudo systemctl status medistock-frontend
sudo systemctl status cruz-amarilla
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Ver logs en vivo

```bash
sudo journalctl -u medistock-backend -f
sudo journalctl -u medistock-frontend -f
sudo tail -f /var/log/nginx/medistock-error.log
```

### Reiniciar servicios después de un cambio

```bash
sudo systemctl restart medistock-backend
sudo systemctl restart medistock-frontend
sudo systemctl restart cruz-amarilla
```

### Actualizar código

```bash
cd /home/ubuntu/medistock
git pull
cd backend && ./venv/bin/pip install -r requirements.txt
cd ../frontend && npm ci && npm run build
cd ../consumidor-externo && npm ci && npm run build
sudo systemctl restart medistock-backend medistock-frontend cruz-amarilla
```

### Acceder a la BD

```bash
sudo -u postgres psql -d medistock
```

---

## Troubleshooting

### "Cannot connect" en el navegador
- Verifica que la IP sea la pública de EC2, no la privada.
- Verifica que el Security Group de la instancia tenga puerto 80 abierto.
- `sudo systemctl status nginx` — ¿está corriendo?

### Backend no responde
```bash
sudo journalctl -u medistock-backend -n 50
```
Revisa que `.env` esté bien configurado y que PostgreSQL esté arriba.

### Frontend muestra error de API
- Verifica que `NEXT_PUBLIC_API_URL` en `frontend/.env.local` apunte a la IP pública.
- Si lo cambias, hay que hacer `npm run build` y `systemctl restart medistock-frontend`.

### Webhook de MercadoPago no llega
- Asegúrate que tu URL pública sea accesible desde internet.
- En MercadoPago, configura como URL de notificación: `http://TU-IP/api/v1/pagos/webhook`.

---

## Costos

- **t2.micro** + 20GB de storage: **$0** durante los primeros 12 meses (Free Tier).
- Tráfico salida: 100GB/mes gratis, luego ~$0.09/GB.
- **Importante**: cuando termines el proyecto, **detén la instancia** desde la consola para no consumir horas.
