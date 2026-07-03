"""Integración con MercadoPago Chile (Checkout Pro, ambiente Sandbox)."""
import mercadopago
from django.conf import settings


class MercadoPagoClient:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    def crear_preferencia(self, orden_numero: str, descripcion: str, monto: float, comprador_email: str) -> dict:
        preference_data = {
            "items": [{
                "title": descripcion,
                "quantity": 1,
                "unit_price": float(monto),
                "currency_id": "CLP",
            }],
            "payer": {"email": comprador_email},
            "external_reference": orden_numero,
            "back_urls": {
                "success": f"{settings.FRONTEND_URL}/checkout/exito?orden={orden_numero}",
                "failure": f"{settings.FRONTEND_URL}/checkout/exito?orden={orden_numero}&error=1",
                "pending": f"{settings.FRONTEND_URL}/checkout/exito?orden={orden_numero}&pendiente=1",
            },
            "auto_return": "approved",
            "notification_url": f"{settings.BACKEND_URL}/api/v1/pagos/webhook",
        }
        respuesta = self.sdk.preference().create(preference_data)
        return respuesta["response"]

    def consultar_pago(self, payment_id: str) -> dict:
        respuesta = self.sdk.payment().get(payment_id)
        return respuesta["response"]


mp_client = MercadoPagoClient()
