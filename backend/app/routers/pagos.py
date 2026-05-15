"""Router de pagos: iniciar pago en MercadoPago, webhook, auditoria."""
from fastapi import APIRouter, Depends, Query, Request

from app.core.enums import EstadoPago, RolUsuario
from app.routers.deps import DbSession, UsuarioAutenticado, requiere_roles
from app.schemas import AuditoriaPago, IniciarPagoResponse, PagoRead
from app.services import PagoService

router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos"])


@router.post("/iniciar/{orden_id}", response_model=IniciarPagoResponse)
def iniciar_pago(orden_id: int, db: DbSession, usuario: UsuarioAutenticado):
    """Crea una preferencia en MercadoPago y retorna la URL de checkout."""
    return PagoService(db).iniciar_pago(orden_id, usuario)


@router.post("/webhook")
async def webhook_mercadopago(
    request: Request, db: DbSession, id: str = Query(""), topic: str = Query("")
):
    """Webhook que MercadoPago llama cuando cambia el estado de un pago."""
    body = await request.json() if request.headers.get("content-length") else {}
    payment_id = body.get("data", {}).get("id") or id
    if payment_id and (topic == "payment" or body.get("type") == "payment"):
        PagoService(db).procesar_webhook(str(payment_id))
    return {"ok": True}


# ============== ANALISTA DE FINANZAS ==============
analista_router = APIRouter(prefix="/api/v1/analista/pagos", tags=["Analista Finanzas"])


@analista_router.get("", response_model=list[PagoRead])
def listar_pagos(
    db: DbSession,
    _=Depends(requiere_roles(RolUsuario.ANALISTA_FINANZAS, RolUsuario.ADMINISTRADOR)),
):
    return PagoService(db).listar_para_auditoria()


@analista_router.post("/{pago_id}/auditar", response_model=PagoRead)
def auditar_pago(
    pago_id: int,
    datos: AuditoriaPago,
    db: DbSession,
    analista: UsuarioAutenticado,
    _=Depends(requiere_roles(RolUsuario.ANALISTA_FINANZAS, RolUsuario.ADMINISTRADOR)),
):
    """Confirma o rechaza un pago manualmente (caso de transferencias B2B)."""
    return PagoService(db).auditar(pago_id, analista, datos.estado)
