"""Router admin: reportes consolidados."""
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select

from backend.app.core.enums import EstadoOrden, EstadoPago, RolUsuario
from backend.app.models import Orden, Pago, Producto, Usuario
from backend.app.routers.deps import DbSession, requiere_roles
from backend.app.schemas import BodegaRead
from backend.app.repositories import BodegaRepository

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


class ReporteDashboard(BaseModel):
    total_productos: int
    total_clientes: int
    total_ordenes: int
    ordenes_pendientes_pago: int
    ordenes_en_preparacion: int
    ordenes_despachadas: int
    pagos_aprobados: int
    monto_total_aprobado: Decimal


@router.get("/dashboard", response_model=ReporteDashboard)
def dashboard(
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.ADMINISTRADOR)),
):
    """Resumen general del negocio."""
    total_productos = db.scalar(select(func.count(Producto.id))) or 0
    total_clientes = db.scalar(
        select(func.count(Usuario.id)).where(
            Usuario.rol.in_(["cliente_institucion", "cliente_paciente"])
        )
    ) or 0
    total_ordenes = db.scalar(select(func.count(Orden.id))) or 0

    pendientes = db.scalar(
        select(func.count(Orden.id)).where(Orden.estado == EstadoOrden.PENDIENTE_PAGO)
    ) or 0
    preparacion = db.scalar(
        select(func.count(Orden.id)).where(Orden.estado == EstadoOrden.EN_PREPARACION)
    ) or 0
    despachadas = db.scalar(
        select(func.count(Orden.id)).where(Orden.estado == EstadoOrden.DESPACHADO)
    ) or 0

    pagos_ok = db.scalar(
        select(func.count(Pago.id)).where(Pago.estado == EstadoPago.APROBADO)
    ) or 0
    monto = db.scalar(
        select(func.coalesce(func.sum(Pago.monto), 0)).where(
            Pago.estado == EstadoPago.APROBADO
        )
    ) or Decimal("0")

    return ReporteDashboard(
        total_productos=total_productos,
        total_clientes=total_clientes,
        total_ordenes=total_ordenes,
        ordenes_pendientes_pago=pendientes,
        ordenes_en_preparacion=preparacion,
        ordenes_despachadas=despachadas,
        pagos_aprobados=pagos_ok,
        monto_total_aprobado=monto,
    )


@router.get("/bodegas", response_model=list[BodegaRead])
def listar_bodegas(
    db: DbSession,
    _=Depends(requiere_roles(
        RolUsuario.ADMINISTRADOR,
        RolUsuario.EJECUTIVO,
        RolUsuario.OPERADOR_LOGISTICO,
    )),
):
    return BodegaRepository(db).list_all()
