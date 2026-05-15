"""Router de ordenes (compras)."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.enums import EstadoOrden, RolUsuario
from app.routers.deps import DbSession, UsuarioAutenticado, requiere_roles
from app.schemas import OrdenCreate, OrdenListItem, OrdenRead
from app.services import OrdenService

router = APIRouter(prefix="/api/v1/ordenes", tags=["Ordenes"])


@router.post("", response_model=OrdenRead, status_code=status.HTTP_201_CREATED)
def crear_orden(
    datos: OrdenCreate,
    db: DbSession,
    usuario: UsuarioAutenticado,
):
    """Crea una nueva orden. Solo clientes pueden hacerlo."""
    if usuario.rol not in (RolUsuario.CLIENTE_INSTITUCION, RolUsuario.CLIENTE_PACIENTE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden crear ordenes",
        )
    return OrdenService(db).crear_orden(usuario, datos)


@router.get("/mis", response_model=list[OrdenListItem])
def mis_ordenes(db: DbSession, usuario: UsuarioAutenticado):
    """Ordenes del cliente actualmente logueado."""
    return OrdenService(db).listar_por_cliente(usuario.id)


@router.get("/{orden_id}", response_model=OrdenRead)
def detalle_orden(orden_id: int, db: DbSession, usuario: UsuarioAutenticado):
    orden = OrdenService(db).obtener(orden_id)
    # Solo el cliente dueño o roles internos pueden verla
    if orden.cliente_id != usuario.id and usuario.rol in (
        RolUsuario.CLIENTE_INSTITUCION,
        RolUsuario.CLIENTE_PACIENTE,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta orden"
        )
    return orden


# ============== EJECUTIVO: aprobar ordenes institucionales ==============
ejecutivo_router = APIRouter(prefix="/api/v1/ejecutivo/ordenes", tags=["Ejecutivo"])


@ejecutivo_router.get("/pendientes", response_model=list[OrdenRead])
def ordenes_pendientes_aprobacion(
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.EJECUTIVO, RolUsuario.ADMINISTRADOR)),
):
    return OrdenService(db).listar_pendientes_aprobacion()


@ejecutivo_router.post("/{orden_id}/aprobar", response_model=OrdenRead)
def aprobar_orden(
    orden_id: int,
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.EJECUTIVO, RolUsuario.ADMINISTRADOR)),
):
    return OrdenService(db).aprobar_por_ejecutivo(orden_id)


# ============== OPERADOR LOGISTICO ==============
operador_router = APIRouter(prefix="/api/v1/operador/ordenes", tags=["Operador Logistico"])


@operador_router.get("/priorizadas", response_model=list[OrdenRead])
def ordenes_priorizadas(
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.OPERADOR_LOGISTICO, RolUsuario.ADMINISTRADOR)),
):
    """Ordenes pagadas ordenadas por urgencia medica (alta -> baja)."""
    return OrdenService(db).listar_para_operador()


@operador_router.post("/{orden_id}/preparar", response_model=OrdenRead)
def marcar_en_preparacion(
    orden_id: int,
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.OPERADOR_LOGISTICO, RolUsuario.ADMINISTRADOR)),
):
    return OrdenService(db).cambiar_estado(orden_id, EstadoOrden.EN_PREPARACION)


@operador_router.post("/{orden_id}/despachar", response_model=OrdenRead)
def marcar_despachada(
    orden_id: int,
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.OPERADOR_LOGISTICO, RolUsuario.ADMINISTRADOR)),
):
    """Despacha la orden. Genera un tracking simulado (sin API externa por ahora)."""
    return OrdenService(db).cambiar_estado(orden_id, EstadoOrden.DESPACHADO)


@operador_router.post("/{orden_id}/entregar", response_model=OrdenRead)
def marcar_entregada(
    orden_id: int,
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.OPERADOR_LOGISTICO, RolUsuario.ADMINISTRADOR)),
):
    return OrdenService(db).cambiar_estado(orden_id, EstadoOrden.ENTREGADO)


# ============== ADMIN: ver todas ==============
admin_router = APIRouter(prefix="/api/v1/admin/ordenes", tags=["Admin"])


@admin_router.get("", response_model=list[OrdenRead])
def listar_todas(
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.ADMINISTRADOR)),
):
    return OrdenService(db).listar_todas()
