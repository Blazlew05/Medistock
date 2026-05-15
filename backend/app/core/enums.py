"""Enumeraciones del dominio."""
from enum import Enum


class RolUsuario(str, Enum):
    CLIENTE_INSTITUCION = "cliente_institucion"
    CLIENTE_PACIENTE = "cliente_paciente"
    ADMINISTRADOR = "administrador"
    EJECUTIVO = "ejecutivo"
    OPERADOR_LOGISTICO = "operador_logistico"
    ANALISTA_FINANZAS = "analista_finanzas"


class EstadoOrden(str, Enum):
    PENDIENTE_PAGO = "pendiente_pago"
    PAGO_CONFIRMADO = "pago_confirmado"
    EN_PREPARACION = "en_preparacion"
    DESPACHADO = "despachado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class EstadoPago(str, Enum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    EN_PROCESO = "en_proceso"


class Urgencia(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class TipoDespacho(str, Enum):
    EXPRESS = "express"
    NORMAL = "normal"


# Roles internos (ven el panel administrativo)
ROLES_INTERNOS = {
    RolUsuario.ADMINISTRADOR,
    RolUsuario.EJECUTIVO,
    RolUsuario.OPERADOR_LOGISTICO,
    RolUsuario.ANALISTA_FINANZAS,
}

# Roles cliente (compran)
ROLES_CLIENTE = {
    RolUsuario.CLIENTE_INSTITUCION,
    RolUsuario.CLIENTE_PACIENTE,
}
