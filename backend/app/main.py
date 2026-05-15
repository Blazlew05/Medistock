"""Aplicacion FastAPI principal de MEDISTOCK."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import admin, auth, ordenes, pagos, productos

app = FastAPI(
    title="MEDISTOCK API",
    description=(
        "API de la distribuidora MEDISTOCK. Expone catalogo de productos, precios "
        "y stock en tiempo real para sistemas externos (ERPs de clinicas)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(productos.public_router)
app.include_router(productos.admin_router)
app.include_router(productos.ejecutivo_router)
app.include_router(ordenes.router)
app.include_router(ordenes.ejecutivo_router)
app.include_router(ordenes.operador_router)
app.include_router(ordenes.admin_router)
app.include_router(pagos.router)
app.include_router(pagos.analista_router)
app.include_router(admin.router)


@app.get("/", tags=["Salud"])
def root():
    return {
        "servicio": "MEDISTOCK API",
        "version": "1.0.0",
        "estado": "operativo",
        "docs": "/docs",
    }


@app.get("/health", tags=["Salud"])
def health():
    return {"status": "ok"}
