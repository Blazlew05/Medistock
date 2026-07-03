from django.conf import settings
from django.db import models

from ordenes.models import Orden


class EstadoPago(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    APROBADO = "aprobado", "Aprobado"
    RECHAZADO = "rechazado", "Rechazado"
    EN_PROCESO = "en_proceso", "En proceso"


class Gateway(models.TextChoices):
    MERCADOPAGO = "mercadopago", "MercadoPago"
    WEBPAY = "webpay", "Webpay Plus"


class Pago(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name="pagos")
    gateway = models.CharField(max_length=20, choices=Gateway.choices, default=Gateway.MERCADOPAGO)
    mercadopago_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    preference_id = models.CharField(max_length=100, blank=True, null=True)
    token_webpay = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    monto = models.DecimalField(max_digits=12, decimal_places=0)
    estado = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    metodo = models.CharField(max_length=50, blank=True, null=True)
    auditado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="pagos_auditados"
    )
    auditado_en = models.DateTimeField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pago #{self.id} ({self.gateway}) - {self.orden.numero}"
