import uuid
from datetime import datetime, timezone

from django.db import transaction
from rest_framework.exceptions import ValidationError

from productos.models import Producto
from usuarios.models import RolUsuario

from .models import COSTO_ENVIO, EstadoOrden, ItemOrden, Orden


def _generar_numero():
    # Fecha a segundos + sufijo aleatorio para garantizar unicidad incluso
    # cuando se crean varias órdenes dentro del mismo segundo.
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"OC-{ts}{uuid.uuid4().hex[:4].upper()}"


@transaction.atomic
def crear_orden(cliente, items_data, tipo_despacho, urgencia, direccion_envio, notas=None):
    if not items_data:
        raise ValidationError("La orden debe tener al menos un producto")

    subtotal = 0
    items_construidos = []
    for item in items_data:
        try:
            producto = Producto.objects.select_for_update().get(id=item["producto_id"], activo=True)
        except Producto.DoesNotExist:
            raise ValidationError(f"Producto {item['producto_id']} no existe")

        cantidad = item["cantidad"]
        if producto.stock_total < cantidad:
            raise ValidationError(f"Stock insuficiente para {producto.nombre}")

        item_subtotal = producto.precio * cantidad
        subtotal += item_subtotal
        items_construidos.append((producto, cantidad, item_subtotal))

    costo_envio = COSTO_ENVIO[tipo_despacho]
    total = subtotal + costo_envio

    orden = Orden.objects.create(
        numero=_generar_numero(),
        cliente=cliente,
        urgencia=urgencia,
        tipo_despacho=tipo_despacho,
        direccion_envio=direccion_envio,
        subtotal=subtotal,
        costo_envio=costo_envio,
        total=total,
        notas=notas,
        # Pacientes (B2C) se auto-aprueban; instituciones (B2B) requieren aprobación del ejecutivo.
        aprobada_por_ejecutivo=(cliente.rol == RolUsuario.CLIENTE_PACIENTE),
    )
    for producto, cantidad, item_subtotal in items_construidos:
        ItemOrden.objects.create(
            orden=orden,
            producto=producto,
            nombre_producto=producto.nombre,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=item_subtotal,
        )
    return orden


def cambiar_estado(orden, nuevo_estado):
    orden.estado = nuevo_estado
    if nuevo_estado == EstadoOrden.DESPACHADO and not orden.tracking_simulado:
        orden.tracking_simulado = f"MED-{orden.numero[-8:]}"
    orden.save()
    return orden
