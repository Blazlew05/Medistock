# MEDISTOCK · Distribuidora de Insumos Clínicos

Plataforma full-stack para la distribuidora MEDISTOCK. Proyecto académico de
**Integración de Plataformas (ASY5131)**, Evaluación Parcial 2.

---

## Arquitectura

```
┌─────────────────┐         ┌─────────────────┐
│  Frontend WEB   │         │ Cruz Amarilla   │
│  Next.js :3000  │         │ Next.js :3001   │
│ (cliente+admin) │         │ (consumidor ext)│
└────────┬────────┘         └────────┬────────┘
         │                           │
         │     HTTPS/HTTP            │
         └─────────────┬─────────────┘
                       │
              ┌────────▼────────┐
              │  MEDISTOCK API  │
              │  FastAPI :8000  │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐  ┌──────▼──────┐ ┌────▼─────┐
   │ Postgres│  │ MercadoPago │ │  Webhook │
   │   DB    │  │  Sandbox CL │ │ callback │
   └─────────┘  └─────────────┘ └──────────┘
```

### Integraciones (3 sistemas)

1. **API REST propia de MEDISTOCK** — productor (Python + FastAPI + PostgreSQL).
2. **MercadoPago Chile** — consumidor (pasarela de pagos sandbox).
3. **Sitio "Farmacia Cruz Amarilla"** — consumidor de la API propia (simula un ERP externo / farmacia asociada que consulta catálogo y precios en tiempo real).

---

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, Alembic, JWT |
| BD | PostgreSQL 14+ |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Pagos | MercadoPago Chile (sandbox) |
| Deploy | AWS EC2 t2.micro, Nginx, systemd |

---

## Estructura del repo

```
medistock/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── core/         # config, security, database, enums
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── repositories/ # Acceso a BD
│   │   ├── services/     # Logica de negocio
│   │   ├── routers/      # Endpoints
│   │   └── integrations/ # MercadoPago client
│   ├── seed.py
│   └── requirements.txt
├── frontend/          # Sitio principal Next.js
│   ├── app/              # Pages (App Router)
│   ├── components/
│   └── lib/
├── consumidor-externo/  # Sitio Cruz Amarilla (consume la API)
├── deploy/            # Scripts y configs de deploy
│   ├── setup.sh
│   ├── nginx.conf
│   └── systemd/
├── docs/              # Documentación
├── postman/           # Coleccion Postman
└── README.md
```

---

## Desarrollo local

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
# .\venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
# Edita .env y configura DATABASE_URL y credenciales MercadoPago

python seed.py             # crea tablas + datos demo
uvicorn app.main:app --reload
```

Backend disponible en **http://localhost:8000** ·
Swagger UI: **http://localhost:8000/docs**

### 2. Frontend principal

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Disponible en **http://localhost:3000**

### 3. Sitio Cruz Amarilla

```bash
cd consumidor-externo
cp .env.example .env.local
npm install
npm run dev
```

Disponible en **http://localhost:3001**

---

## Roles del sistema (6 roles)

| Rol | Email demo | Password | Vista |
|-----|------------|----------|-------|
| Administrador | admin@medistock.cl | admin123 | `/admin` |
| Ejecutivo | ejecutivo@medistock.cl | ejec123 | `/ejecutivo` |
| Operador logístico | operador@medistock.cl | oper123 | `/operador` |
| Analista finanzas | analista@medistock.cl | anal123 | `/analista` |
| Cliente institución | compras@clinicalasandes.cl | clinica123 | `/catalogo` |
| Cliente paciente | paciente@gmail.com | paciente123 | `/catalogo` |

---

## Flujo end-to-end

1. **Cliente paciente** ve el catálogo y agrega al carrito.
2. En **checkout** completa dirección y elige tipo de despacho.
3. Se crea la **orden** y se inicia un pago en **MercadoPago**.
4. El cliente paga en sandbox (tarjetas de prueba abajo).
5. MercadoPago llama al **webhook** del backend → la orden pasa a `pago_confirmado`.
6. El **operador logístico** ve la orden priorizada y la marca como `en_preparacion` → `despachado`.
7. El **analista de finanzas** audita el pago.
8. El **administrador** ve todo desde el dashboard.

### Para clientes institución (B2B)
La orden requiere **aprobación del ejecutivo de cuentas** antes de proceder al pago.

---

## Tarjetas de prueba MercadoPago Chile

| Marca | Número | CVV | Fecha |
|-------|--------|-----|-------|
| Mastercard | 5031 7557 3453 0604 | 123 | 11/30 |
| Visa | 4168 8188 4444 7115 | 123 | 11/30 |
| American Express | 3711 803032 57522 | 1234 | 11/30 |

Documento: **12345678-5** · Nombre titular: cualquiera

Para forzar resultados específicos:
- `APRO` → pago aprobado
- `OTHE` → rechazado por error general
- `CONT` → pendiente

Ver [docs/MERCADOPAGO_SETUP.md](docs/MERCADOPAGO_SETUP.md) para obtener credenciales sandbox.

---

## Deploy en AWS EC2

Ver guía paso a paso: [docs/DEPLOY.md](docs/DEPLOY.md).

Resumen ultra-corto:

```bash
# 1. Lanza una EC2 t2.micro Ubuntu 22.04, abre puertos 22 y 80
# 2. SSH a la instancia
ssh -i tu-llave.pem ubuntu@TU-IP

# 3. Clona y ejecuta
git clone https://github.com/tu-usuario/medistock.git
cd medistock
sudo bash deploy/setup.sh
```

El script instala todo, crea la BD, hace seed y configura systemd + Nginx.

---

## API Endpoints destacados

### Públicos (sin auth — consumibles por ERPs)

- `GET /api/v1/productos` — lista de productos
- `GET /api/v1/productos/categorias` — categorías
- `GET /api/v1/productos/{codigo}` — detalle por código

### Autenticación

- `POST /api/v1/auth/registro`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/yo`

Ver swagger completo en `/docs`.

---

## Plan de pruebas

Ver [docs/plan-de-pruebas.md](docs/plan-de-pruebas.md).

Colección Postman en [postman/medistock.postman_collection.json](postman/medistock.postman_collection.json).

---

## Autores

Proyecto académico ASY5131 · Integración de Plataformas · 2026.
