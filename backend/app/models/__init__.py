"""Modelos SQLAlchemy del dominio MEDISTOCK."""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import (
    EstadoOrden,
    EstadoPago,
    RolUsuario,
    TipoDespacho,
    Urgencia,
)


def utcnow():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(String(50), nullable=False)
    empresa: Mapped[str | None] = mapped_column(String(150), nullable=True)
    rut: Mapped[str | None] = mapped_column(String(20), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    ordenes: Mapped[list["Orden"]] = relationship(back_populates="cliente")


class Bodega(Base):
    __tablename__ = "bodegas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    stocks: Mapped[list["StockBodega"]] = relationship(back_populates="bodega")


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 0), nullable=False)
    unidad: Mapped[str] = mapped_column(String(30), nullable=False, default="unidad")
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    requiere_receta: Mapped[bool] = mapped_column(Boolean, default=False)
    es_critico: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    stocks: Mapped[list["StockBodega"]] = relationship(back_populates="producto")

    @property
    def stock_total(self) -> int:
        return sum(s.cantidad for s in self.stocks)


class StockBodega(Base):
    __tablename__ = "stock_bodegas"
    __table_args__ = (UniqueConstraint("producto_id", "bodega_id", name="uq_producto_bodega"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    bodega_id: Mapped[int] = mapped_column(ForeignKey("bodegas.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lote: Mapped[str | None] = mapped_column(String(50), nullable=True)
    caducidad: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    producto: Mapped[Producto] = relationship(back_populates="stocks")
    bodega: Mapped[Bodega] = relationship(back_populates="stocks")


class Orden(Base):
    __tablename__ = "ordenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    estado: Mapped[EstadoOrden] = mapped_column(String(30), default=EstadoOrden.PENDIENTE_PAGO)
    urgencia: Mapped[Urgencia] = mapped_column(String(20), default=Urgencia.MEDIA)
    tipo_despacho: Mapped[TipoDespacho] = mapped_column(String(20), default=TipoDespacho.NORMAL)
    direccion_envio: Mapped[str] = mapped_column(String(255), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    costo_envio: Mapped[Decimal] = mapped_column(Numeric(10, 0), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    aprobada_por_ejecutivo: Mapped[bool] = mapped_column(Boolean, default=False)
    tracking_simulado: Mapped[str | None] = mapped_column(String(100), nullable=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    actualizada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    cliente: Mapped[Usuario] = relationship(back_populates="ordenes")
    items: Mapped[list["ItemOrden"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )
    pagos: Mapped[list["Pago"]] = relationship(back_populates="orden")


class ItemOrden(Base):
    __tablename__ = "items_orden"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    nombre_producto: Mapped[str] = mapped_column(String(200), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 0), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)

    orden: Mapped[Orden] = relationship(back_populates="items")
    producto: Mapped[Producto] = relationship()


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    mercadopago_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    preference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 0), nullable=False)
    estado: Mapped[EstadoPago] = mapped_column(String(30), default=EstadoPago.PENDIENTE)
    metodo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    auditado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    auditado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    orden: Mapped[Orden] = relationship(back_populates="pagos")
