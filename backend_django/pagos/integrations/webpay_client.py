"""Integración con Transbank Webpay Plus Chile (pasarela secundaria, sandbox de integración).

Documentación: https://www.transbankdevelopers.cl/
"""
from django.conf import settings
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.webpay.webpay_plus.transaction import Transaction


class WebpayClient:
    def __init__(self):
        # Sin credenciales configuradas, se usa el ambiente de integración (sandbox) por defecto.
        if getattr(settings, "WEBPAY_COMMERCE_CODE", "") and getattr(settings, "WEBPAY_API_KEY", ""):
            options = WebpayOptions(
                commerce_code=settings.WEBPAY_COMMERCE_CODE,
                api_key=settings.WEBPAY_API_KEY,
                integration_type=IntegrationType.LIVE,
            )
        else:
            options = WebpayOptions(
                commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
                api_key=IntegrationApiKeys.WEBPAY,
                integration_type=IntegrationType.TEST,
            )
        self.tx = Transaction(options)

    def crear_transaccion(self, orden_numero: str, monto: float, session_id: str = "session_medistock") -> dict:
        return_url = f"{settings.BACKEND_URL}/api/v1/pagos/webpay/callback"
        response = self.tx.create(
            buy_order=orden_numero,
            session_id=session_id,
            amount=int(monto),
            return_url=return_url,
        )
        return {"token": response["token"], "url": response["url"]}

    def confirmar_transaccion(self, token: str) -> dict:
        return self.tx.commit(token=token)


webpay_client = WebpayClient()
