"""Integracion con Transbank Webpay Plus Chile (Mall/Normal Sandbox).

Documentacion: https://www.transbankdevelopers.cl/
"""
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType

from backend.app.core.config import settings


class WebpayClient:
    """Cliente que encapsula la SDK oficial de Transbank Webpay Plus."""

    def __init__(self):
        # Transbank usa por defecto su entorno de INTEGRACIÓN (Sandbox) si no se configuran credenciales.
        # En producción se debe usar settings.WEBPAY_COMMERCE_CODE y settings.WEBPAY_API_KEY.
        if not getattr(settings, "WEBPAY_API_KEY", None):
            self.tx = Transaction()  # Carga credenciales demo automáticamente
        else:
            # Configuración para producción en AWS
            self.tx = Transaction().configure_for_production(
                commerce_code=settings.WEBPAY_COMMERCE_CODE,
                api_key=settings.WEBPAY_API_KEY
            )

    def crear_transaccion(
        self,
        orden_numero: str,
        monto: float,
        session_id: str = "session_medistock",
    ) -> dict:
        """Inicia una transacción en Webpay Plus.
        
        Retorna el 'token' y la 'url' a la que el frontend debe redirigir al usuario.
        """
        # URLs de retorno a tu API de FastAPI para capturar el resultado
        return_url = f"{settings.BACKEND_URL}/api/v1/pagos/webpay-callback"

        if getattr(settings, "MOCK_PAGOS", True) and not getattr(settings, "WEBPAY_API_KEY", None):
            # Modo desarrollo/simulado opcional
            return {
                "token": f"FAKE-TOKEN-{orden_number}",
                "url": f"{settings.FRONTEND_URL}/checkout/mock?orden={orden_numero}"
            }

        try:
            # Los montos en CLP para Webpay deben ser enteros obligatoriamente
            monto_int = int(monto)

            response = self.tx.create(
                buy_order=orden_numero,
                session_id=session_id,
                amount=monto_int,
                return_url=return_url
            )
            
            return {
                "token": response['token'],
                "url": response['url']
            }
        except Exception as e:
            raise RuntimeError(f"Error al inicializar Webpay Plus: {str(e)}")

    def confirmar_transaccion(self, token: str) -> dict:
        """Confirma el pago (Commit) ante Transbank usando el token recibido en el callback."""
        if "FAKE-TOKEN" in token:
            return {"status": "AUTHORIZED", "buy_order": token.split("-")[-1], "amount": 1000}

        try:
            # Este paso es OBLIGATORIO en Webpay para capturar el dinero
            response = self.tx.commit(token=token)
            return response
        except Exception as e:
            raise RuntimeError(f"Error al confirmar la transacción en Webpay: {str(e)}")


webpay_client = WebpayClient()