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

## Integraciones (3 Sistemas Conectados)
1. **API REST Propia de MEDISTOCK (Productor):** Construida en Python con FastAPI y PostgreSQL como motor de persistencia.
2. **MercadoPago Chile (Consumidor Pasarela):** Integración nativa de checkout para transacciones en ambiente Sandbox.
3. **Sitio "Farmacia Cruz Amarilla" (Consumidor ERP):** Aplicación secundaria que simula un ERP externo o farmacia asociada que consulta stock, catálogo y precios en tiempo real mediante endpoints públicos.

---

Stack Tecnológico

| Capa | Tecnologías | Contenedor Docker | Puertos |
| :--- | :--- | :--- | :--- |
| **Base de Datos** | PostgreSQL 14+ | `medistock_db` | `5432:5432` |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Alembic, JWT | `medistock_api` | `8000:8000` |
| **Frontend Principal** | Next.js 14 (App Router), TS, Tailwind CSS | `medistock_main_web` | `3000:3000` |
| **Consumidor Externo** | Next.js 14, TypeScript (Cruz Amarilla) | `medistock_cruz_amarilla` | `3001:3001` |
| **Orquestación** | Docker & Docker Compose | - | - |
| **Despliegue / Cloud** | AWS EC2 (t2.micro), Nginx, Systemd, Ubuntu 22.04 | - | - |

---

Estructura del Repositorio

```text
medistock/
├── docker-compose.yml        # Orquestación de todo el ecosistema multi-contenedor
├── backend/                  # API FastAPI (Productor)
│   ├── app/
│   │   ├── core/             # Configuración, seguridad, conexión a BD y Enums
│   │   ├── models/           # Modelos ORM (SQLAlchemy)
│   │   ├── schemas/          # Esquemas de validación de datos (Pydantic)
│   │   ├── routers/          # Controladores y Endpoints de la API
│   │   └── integrations/     # Cliente SDK de MercadoPago
│   ├── seed.py               # Script de inicialización de datos demo
│   ├── requirements.txt      # Dependencias del Backend Python
│   └── Dockerfile            # Configuración de imagen para el Backend
├── frontend/                 # Aplicación Principal Next.js 14
│   ├── app/                  # Módulos y ruteo (App Router)
│   ├── components/           # Componentes UI reutilizables
│   └── lib/                  # Clientes de API y utilidades
├── consumidor-externo/       # Portal "Farmacia Cruz Amarilla" (Cliente B2B)
├── deploy/                   # Automatización y scripts de despliegue productivo
│   ├── setup.sh              # Script de aprovisionamiento en AWS
│   └── nginx.conf            # Configuración del proxy inverso Nginx
├── docs/                     # Guías detalladas de configuración externa
└── postman/                  # Colecciones de prueba de endpoints (Postman)

--

## Desarrollo Local (Ecosistema Docker Unificado)

### 1. Configurar Variables de Entorno
Antes de encender los servicios, asegúrese de copiar las plantillas de configuración `.env.example` a sus archivos reales en cada carpeta y rellenar las credenciales de MercadoPago en el backend:

```bash
# Configurar entorno del Backend
cp backend/.env.example backend/.env

# Configurar entornos de los Frontends
cp frontend/.env.example frontend/.env.local
cp consumidor-externo/.env.example consumidor-externo/.env.local

python seed.py             # crea tablas + datos demo
uvicorn app.main:app --reload
```
### Integraciones (4 sistemas en total)
1. **API REST propia de MEDISTOCK** — productor (Python + FastAPI + PostgreSQL).
2. **MercadoPago Chile** — consumidor (pasarela de pagos sandbox principal).
3. **Transbank Webpay Plus** — consumidor (pasarela de pagos sandbox secundaria integrada para redundancia).
4. **Sitio "Farmacia Cruz Amarilla"** — consumidor de la API propia (simula un ERP externo).
Backend disponible en **http://localhost:8000** ·
Swagger UI: **http://localhost:8000/docs**

### 2. Frontend principal

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```
### Levantar el Ecosistema Completo

docker compose up -d --build

### Población Inicial de Datos (Seed)

docker compose exec backend python seed.py

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
