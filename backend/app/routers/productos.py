"""Router de productos.

La API publica (sin auth) es la que consumen sistemas externos (ERPs de clinicas,
sitio "Cruz Amarilla"). Cumple el requisito clave del caso de estudio.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.enums import RolUsuario
from app.routers.deps import DbSession, requiere_roles
from app.schemas import (
    ProductoConStockDetalle,
    ProductoCreate,
    ProductoPublico,
    ProductoRead,
    ProductoUpdate,
    StockPorBodega,
)
from app.services import ProductoService

# Router publico (sin autenticacion) - lo consumen ERPs
public_router = APIRouter(prefix="/api/v1/productos", tags=["Productos (Publico/ERP)"])

# Router admin (requiere autenticacion)
admin_router = APIRouter(prefix="/api/v1/admin/productos", tags=["Productos (Admin)"])


# ============== ENDPOINTS PUBLICOS (consumibles por ERPs) ==============
@public_router.get("", response_model=list[ProductoPublico])
def listar_productos_publicos(
    db: DbSession,
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
):
    """Lista publica de productos con stock en tiempo real.

    Consumible por sistemas externos (ERPs, farmacias asociadas).
    """
    return ProductoService(db).listar(categoria=categoria)


@public_router.get("/categorias", response_model=list[str])
def listar_categorias(db: DbSession):
    """Lista de categorias disponibles."""
    return ProductoService(db).listar_categorias()


@public_router.get("/{codigo_producto}", response_model=ProductoPublico)
def obtener_producto_por_codigo(codigo_producto: str, db: DbSession):
    """Detalle de un producto por su codigo. Endpoint clave para ERPs.

    Ejemplo del caso de estudio:
    GET /api/v1/productos/{codigo_producto}
    """
    return ProductoService(db).obtener_por_codigo(codigo_producto)


# ============== ENDPOINTS ADMIN ==============
@admin_router.get("", response_model=list[ProductoRead])
def listar_productos_admin(
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.ADMINISTRADOR)),
):
    """Lista completa de productos (incluye inactivos)."""
    return ProductoService(db).repo.list_all(solo_activos=False)


@admin_router.post("", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto(
    datos: ProductoCreate,
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.ADMINISTRADOR)),
):
    return ProductoService(db).crear(datos)


@admin_router.put("/{producto_id}", response_model=ProductoRead)
def actualizar_producto(
    producto_id: int,
    datos: ProductoUpdate,
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.ADMINISTRADOR)),
):
    return ProductoService(db).actualizar(producto_id, datos)


# ============== EJECUTIVO: stock multi-bodega ==============
ejecutivo_router = APIRouter(prefix="/api/v1/ejecutivo", tags=["Ejecutivo"])


@ejecutivo_router.get("/productos/{producto_id}/stock", response_model=ProductoConStockDetalle)
def stock_por_bodega(
    producto_id: int,
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.EJECUTIVO, RolUsuario.ADMINISTRADOR)),
):
    """Detalle de stock cruzado entre todas las bodegas para un producto."""
    producto = ProductoService(db).obtener_por_id(producto_id)
    detalle = ProductoConStockDetalle.model_validate(producto)
    detalle.stock_por_bodega = [
        StockPorBodega(
            bodega_id=s.bodega.id,
            bodega_nombre=s.bodega.nombre,
            bodega_region=s.bodega.region,
            cantidad=s.cantidad,
            lote=s.lote,
        )
        for s in producto.stocks
    ]
    return detalle
