from django.conf import settings
from django.db import models

from productos.models import Producto


class EstadoOrden(models.TextChoices):
    PENDIENTE_PAGO = "pendiente_pago", "Pendiente de pago"
    PAGO_CONFIRMADO = "pago_confirmado", "Pago confirmado"
    EN_PREPARACION = "en_preparacion", "En preparación"
    DESPACHADO = "despachado", "Despachado"
    ENTREGADO = "entregado", "Entregado"
    CANCELADO = "cancelado", "Cancelado"


class Urgencia(models.TextChoices):
    ALTA = "alta", "Alta"
    MEDIA = "media", "Media"
    BAJA = "baja", "Baja"


class TipoDespacho(models.TextChoices):
    EXPRESS = "express", "Express"
    NORMAL = "normal", "Normal"


COSTO_ENVIO = {
    TipoDespacho.EXPRESS: 5990,
    TipoDespacho.NORMAL: 2990,
}


class Orden(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ordenes")
    estado = models.CharField(max_length=30, choices=EstadoOrden.choices, default=EstadoOrden.PENDIENTE_PAGO)
    urgencia = models.CharField(max_length=10, choices=Urgencia.choices, default=Urgencia.MEDIA)
    tipo_despacho = models.CharField(max_length=10, choices=TipoDespacho.choices, default=TipoDespacho.NORMAL)
    direccion_envio = models.CharField(max_length=255)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    costo_envio = models.DecimalField(max_digits=12, decimal_places=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    notas = models.TextField(blank=True, null=True)
    aprobada_por_ejecutivo = models.BooleanField(default=False)
    tracking_simulado = models.CharField(max_length=50, blank=True, null=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creada_en"]

    def __str__(self):
        return f"Orden {self.numero} - {self.estado}"


class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="items_orden")
    nombre_producto = models.CharField(max_length=255)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto}"
