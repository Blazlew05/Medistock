from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, iniciar_pago_webpay, webpay_callback

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webpay/iniciar/', iniciar_pago_webpay, name='iniciar_pago'),
    path('webpay-callback/', webpay_callback, name='webpay_callback'),
]