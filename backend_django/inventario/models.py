from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField()  # Entero para que calce directo con pesos chilenos (CLP)
    stock = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos', null=True, blank=True)
    orden_numero = models.CharField(max_length=100, unique=True)
    monto_total = models.IntegerField()
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE')
    token_webpay = models.CharField(max_length=255, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"Orden {self.orden_numero} - {self.estado_pago}"