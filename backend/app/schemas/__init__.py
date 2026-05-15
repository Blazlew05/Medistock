"""Schemas Pydantic para validacion de la API."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import (
    EstadoOrden,
    EstadoPago,
    RolUsuario,
    TipoDespacho,
    Urgencia,
)


# ---------- Usuario ----------
class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    rol: RolUsuario
    empresa: Optional[str] = None
    rut: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=6)


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead


# ---------- Bodega ----------
class BodegaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    nombre: str
    region: str
    direccion: str
    activa: bool


class StockPorBodega(BaseModel):
    bodega_id: int
    bodega_nombre: str
    bodega_region: str
    cantidad: int
    lote: Optional[str] = None


# ---------- Producto ----------
class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: str
    categoria: str
    precio: Decimal
    unidad: str = "unidad"
    imagen_url: Optional[str] = None
    requiere_receta: bool = False
    es_critico: bool = False


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[Decimal] = None
    unidad: Optional[str] = None
    imagen_url: Optional[str] = None
    requiere_receta: Optional[bool] = None
    es_critico: Optional[bool] = None
    activo: Optional[bool] = None


class ProductoRead(ProductoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    stock_total: int
    creado_en: datetime


class ProductoPublico(BaseModel):
    """Schema publico expuesto a sistemas externos (ERPs, Cruz Amarilla)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    nombre: str
    descripcion: str
    categoria: str
    precio: Decimal
    unidad: str
    stock_total: int
    requiere_receta: bool
    imagen_url: Optional[str] = None


class ProductoConStockDetalle(ProductoRead):
    stock_por_bodega: list[StockPorBodega] = []


# ---------- Carrito / Items ----------
class ItemOrdenCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class ItemOrdenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


# ---------- Orden ----------
class OrdenCreate(BaseModel):
    items: list[ItemOrdenCreate]
    tipo_despacho: TipoDespacho = TipoDespacho.NORMAL
    urgencia: Urgencia = Urgencia.MEDIA
    direccion_envio: str
    notas: Optional[str] = None


class OrdenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    cliente_id: int
    estado: EstadoOrden
    urgencia: Urgencia
    tipo_despacho: TipoDespacho
    direccion_envio: str
    subtotal: Decimal
    costo_envio: Decimal
    total: Decimal
    notas: Optional[str] = None
    aprobada_por_ejecutivo: bool
    tracking_simulado: Optional[str] = None
    creada_en: datetime
    items: list[ItemOrdenRead]


class OrdenListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    estado: EstadoOrden
    urgencia: Urgencia
    tipo_despacho: TipoDespacho
    total: Decimal
    creada_en: datetime


# ---------- Pago ----------
class PagoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    orden_id: int
    mercadopago_id: Optional[str] = None
    preference_id: Optional[str] = None
    monto: Decimal
    estado: EstadoPago
    metodo: Optional[str] = None
    creado_en: datetime


class IniciarPagoResponse(BaseModel):
    pago_id: int
    preference_id: str
    init_point: str
    sandbox_init_point: str


class AuditoriaPago(BaseModel):
    estado: EstadoPago
    nota: Optional[str] = None
