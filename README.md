# MEDISTOCK · Distribuidora de Insumos Clínicos

Plataforma full-stack para la distribuidora MEDISTOCK. Proyecto académico de
**Integración de Plataformas (ASY5131)**, Evaluación Parcial 2.

---

## Arquitectura

```
┌─────────────────┐         ┌─────────────────┐
│  Frontend WEB   │         │ Cruz Amarilla   │
│  Vite+React     │         │ Next.js :3001   │
│    :5173        │         │ (consumidor ext)│
│ (cliente+admin) │         │                 │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │     HTTPS/HTTP            │
         └─────────────┬─────────────┘
                       │
              ┌────────▼────────┐
              │  MEDISTOCK API  │
              │  Django :8000   │
              └────────┬────────┘
                       │
        ┌──────────────┼───────────────┬──────────────┐
        │              │               │              │
   ┌────▼────┐  ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼────┐
   │ Postgres│  │ MercadoPago │ │Webpay Plus  │ │  Webhook │
   │   DB    │  │  Sandbox CL │ │ (Transbank) │ │ callback │
   └─────────┘  └─────────────┘ └─────────────┘ └──────────┘
```

## Integraciones (4 Sistemas Conectados)
1. **API REST Propia de MEDISTOCK (Productor):** Construida en Python con Django + Django REST Framework y PostgreSQL como motor de persistencia.
2. **MercadoPago Chile (Consumidor Pasarela):** Integración nativa de checkout para transacciones en ambiente Sandbox.
3. **Transbank Webpay Plus (Consumidor Pasarela):** Pasarela de pago sandbox secundaria, integrada como alternativa a MercadoPago.
4. **Sitio "Farmacia Cruz Amarilla" (Consumidor ERP):** Aplicación secundaria que simula un ERP externo o farmacia asociada que consulta stock, catálogo y precios en tiempo real mediante endpoints públicos.

---

Stack Tecnológico

| Capa | Tecnologías | Contenedor Docker | Puertos |
| :--- | :--- | :--- | :--- |
| **Base de Datos** | PostgreSQL 16 | `medistock_db` | `5432:5432` |
| **Backend** | Python 3.12, Django, Django REST Framework, JWT | `medistock_django` | `8000:8000` |
| **Frontend Principal** | React 18 + Vite, React Router, Tailwind CSS | `medistock_react` | `5173:5173` |
| **Consumidor Externo** | Next.js 14, TypeScript (Cruz Amarilla) | `medistock_cruz_amarilla` | `3001:3001` |
| **Orquestación** | Docker & Docker Compose | - | - |
| **Despliegue / Cloud** | AWS EC2 (t2.micro), Nginx, Systemd, Ubuntu 22.04 | - | - |

---

Estructura del Repositorio

```text
medistock/
├── docker-compose.yml        # Orquestación de todo el ecosistema multi-contenedor
├── backend_django/           # API Django (Productor)
│   ├── medistock_core/       # Settings, urls raíz, wsgi/asgi
│   ├── usuarios/             # Modelo de usuario, auth JWT propia, permisos por rol
│   ├── productos/            # Producto, Bodega, StockBodega + seed_demo
│   ├── ordenes/               # Orden, ItemOrden, state machine de fulfillment
│   ├── pagos/                 # Pago + integraciones MercadoPago y Webpay Plus
│   ├── requirements.txt      # Dependencias del Backend Python
│   └── Dockerfile            # Configuración de imagen para el Backend
├── frontend_vite/            # Aplicación Principal React + Vite
│   ├── src/pages/             # Páginas (una por ruta, vía React Router)
│   ├── src/components/        # Navbar, AuthGuard
│   └── src/lib/                # Cliente de API y carrito (localStorage)
├── consumidor-externo/       # Portal "Farmacia Cruz Amarilla" (Cliente B2B)
├── deploy/                   # Automatización y scripts de despliegue productivo
│   ├── setup.sh              # Script de aprovisionamiento en AWS
│   └── nginx.conf            # Configuración del proxy inverso Nginx
├── docs/                     # Guías detalladas de configuración externa
└── postman/                  # Colecciones de prueba de endpoints (Postman)

--

## Desarrollo Local (Ecosistema Docker Unificado)

### 1. Configurar Variables de Entorno
Antes de encender los servicios, copia las plantillas `.env.example` a sus archivos reales y rellena las credenciales de MercadoPago/Webpay en el backend:

```bash
# Configurar entorno del Backend
cp backend_django/.env.example backend_django/.env

# Configurar entornos de los Frontends
cp frontend_vite/.env.example frontend_vite/.env
cp consumidor-externo/.env.example consumidor-externo/.env.local
```

### Integraciones (4 sistemas en total)
1. **API REST propia de MEDISTOCK** — productor (Python + Django REST Framework + PostgreSQL).
2. **MercadoPago Chile** — consumidor (pasarela de pagos sandbox principal).
3. **Transbank Webpay Plus** — consumidor (pasarela de pagos sandbox secundaria integrada para redundancia).
4. **Sitio "Farmacia Cruz Amarilla"** — consumidor de la API propia (simula un ERP externo).

### 2. Levantar el Ecosistema Completo

```bash
docker compose up -d --build
```

Esto levanta `db` (Postgres), `backend_django` (:8000) y `frontend_vite` (:5173).

### 3. Migraciones y Población Inicial de Datos (Seed)

```bash
docker compose exec backend_django python manage.py migrate
docker compose exec backend_django python manage.py seed_demo
```

Backend disponible en **http://localhost:8000** · Admin de Django: **http://localhost:8000/admin**
Frontend principal disponible en **http://localhost:5173**

### 4. Sitio Cruz Amarilla

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

Ver la colección Postman para el resto de endpoints (ejecutivo, operador, analista, admin, pagos).

---

## Plan de pruebas

Ver [docs/plan-de-pruebas.md](docs/plan-de-pruebas.md).

Colección Postman en [postman/medistock.postman_collection.json](postman/medistock.postman_collection.json).

---

## Autores

Proyecto académico ASY5131 · Integración de Plataformas · 2026.
