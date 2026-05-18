"""Integracion con MercadoPago Chile (sandbox).

Documentacion: https://www.mercadopago.cl/developers/es/docs/checkout-pro
"""
import mercadopago

from app.core.config import settings


class MercadoPagoClient:
    """Cliente que encapsula la SDK oficial de MercadoPago."""

    def __init__(self):
        if not settings.MERCADOPAGO_ACCESS_TOKEN:
            self.sdk = None
        else:
            self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    def crear_preferencia(
        self,
        orden_numero: str,
        descripcion: str,
        monto: float,
        comprador_email: str,
    ) -> dict:
        """Crea una preferencia de pago en MercadoPago.

        Retorna un dict con preference_id, init_point y sandbox_init_point.
        """
        if not self.sdk:
            # Modo desarrollo sin credenciales: respuesta simulada
            return {
                "id": f"FAKE-PREF-{orden_numero}",
                "init_point": f"{settings.FRONTEND_URL}/checkout/mock?orden={orden_numero}",
                "sandbox_init_point": f"{settings.FRONTEND_URL}/checkout/mock?orden={orden_numero}",
            }

        preference_data = {
            "items": [
                {
                    "title": descripcion,
                    "quantity": 1,
                    "unit_price": float(monto),
                    "currency_id": "CLP",
                }
            ],
            "payer": {"email": comprador_email},
            "external_reference": orden_numero,
            "back_urls": {
                "success": f"{settings.FRONTEND_URL}/checkout/exito?orden={orden_numero}",
                "failure": f"{settings.FRONTEND_URL}/checkout/error?orden={orden_numero}",
                "pending": f"{settings.FRONTEND_URL}/checkout/pendiente?orden={orden_numero}",
            },
            "auto_return": "approved",
            "notification_url": f"{settings.BACKEND_URL}/api/v1/pagos/webhook",
        }

        result = self.sdk.preference().create(preference_data)
        if result["status"] not in (200, 201):
            raise RuntimeError(f"Error MercadoPago: {result}")
        return result["response"]

    def consultar_pago(self, payment_id: str) -> dict:
        """Consulta el estado de un pago en MercadoPago."""
        if not self.sdk:
            return {"status": "approved", "id": payment_id, "payment_method_id": "visa"}
        result = self.sdk.payment().get(payment_id)
        return result["response"]


mp_client = MercadoPagoClient()
