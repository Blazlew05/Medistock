from django.contrib import admin

from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "orden", "gateway", "monto", "estado", "creado_en")
    list_filter = ("gateway", "estado")
    search_fields = ("orden__numero", "mercadopago_id", "token_webpay")
