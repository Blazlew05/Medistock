from django.urls import path

from . import views

urlpatterns = [
    path("pagos/iniciar/<int:orden_id>", views.IniciarPagoMercadoPagoView.as_view(), name="pagos-iniciar-mercadopago"),
    path("pagos/webhook", views.WebhookMercadoPagoView.as_view(), name="pagos-webhook-mercadopago"),
    path("pagos/webpay/iniciar/<int:orden_id>", views.IniciarPagoWebpayView.as_view(), name="pagos-iniciar-webpay"),
    path("pagos/webpay/callback", views.WebpayCallbackView.as_view(), name="pagos-webpay-callback"),
    path("analista/pagos", views.AnalistaPagosListView.as_view(), name="analista-pagos"),
    path("analista/pagos/<int:pago_id>/auditar", views.AuditarPagoView.as_view(), name="analista-pagos-auditar"),
]
