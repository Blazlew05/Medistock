from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ordenes.models import EstadoOrden, Orden
from usuarios.models import RolUsuario
from usuarios.permissions import IsRole

from .integrations.mercadopago_client import mp_client
from .integrations.webpay_client import webpay_client
from .models import EstadoPago, Gateway, Pago
from .serializers import AuditoriaPagoSerializer, PagoSerializer


def _validar_orden_para_pago(orden, cliente):
    if orden.cliente_id != cliente.id:
        raise PermissionDenied("La orden no pertenece al cliente")
    if not orden.aprobada_por_ejecutivo:
        raise ValidationError("La orden aún no fue aprobada por un ejecutivo")
    if orden.estado != EstadoOrden.PENDIENTE_PAGO:
        raise ValidationError(f"La orden no está pendiente de pago (estado actual: {orden.estado})")


class IniciarPagoMercadoPagoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orden_id):
        orden = get_object_or_404(Orden, id=orden_id)
        _validar_orden_para_pago(orden, request.user)

        respuesta_mp = mp_client.crear_preferencia(
            orden_numero=orden.numero,
            descripcion=f"MEDISTOCK - Orden {orden.numero}",
            monto=float(orden.total),
            comprador_email=request.user.email,
        )

        pago = Pago.objects.create(
            orden=orden,
            gateway=Gateway.MERCADOPAGO,
            preference_id=respuesta_mp["id"],
            monto=orden.total,
            estado=EstadoPago.PENDIENTE,
        )

        return Response({
            "pago_id": pago.id,
            "preference_id": respuesta_mp["id"],
            "init_point": respuesta_mp.get("init_point", ""),
            "sandbox_init_point": respuesta_mp.get("sandbox_init_point", ""),
        })


class WebhookMercadoPagoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        body = request.data if isinstance(request.data, dict) else {}
        payment_id = body.get("data", {}).get("id") or request.query_params.get("id")
        topic = request.query_params.get("topic") or body.get("type")

        if payment_id and topic == "payment":
            self._procesar(str(payment_id))

        return Response({"ok": True})

    def _procesar(self, payment_id):
        info = mp_client.consultar_pago(payment_id)
        external_ref = info.get("external_reference")
        if not external_ref:
            return

        orden = Orden.objects.filter(numero=external_ref).first()
        if not orden:
            return

        pago = orden.pagos.filter(gateway=Gateway.MERCADOPAGO, preference_id__isnull=False).first()
        if not pago:
            return

        pago.mercadopago_id = str(info.get("id"))
        pago.metodo = info.get("payment_method_id")
        mp_status = info.get("status")
        if mp_status == "approved":
            pago.estado = EstadoPago.APROBADO
            orden.estado = EstadoOrden.PAGO_CONFIRMADO
            orden.save()
        elif mp_status == "rejected":
            pago.estado = EstadoPago.RECHAZADO
        else:
            pago.estado = EstadoPago.EN_PROCESO
        pago.save()


class IniciarPagoWebpayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orden_id):
        orden = get_object_or_404(Orden, id=orden_id)
        _validar_orden_para_pago(orden, request.user)

        respuesta = webpay_client.crear_transaccion(
            orden_numero=orden.numero,
            monto=float(orden.total),
        )

        Pago.objects.create(
            orden=orden,
            gateway=Gateway.WEBPAY,
            token_webpay=respuesta["token"],
            monto=orden.total,
            estado=EstadoPago.PENDIENTE,
        )

        return Response({"token": respuesta["token"], "url": respuesta["url"]})


class WebpayCallbackView(APIView):
    """Transbank redirige el navegador del cliente a esta URL (POST) tras el pago."""

    permission_classes = [AllowAny]

    def post(self, request):
        return self._procesar(request)

    def get(self, request):
        return self._procesar(request)

    def _procesar(self, request):
        token = request.data.get("token_ws") or request.query_params.get("token_ws")
        if not token:
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/checkout/exito?error=1")

        pago = Pago.objects.filter(token_webpay=token).first()
        if not pago:
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/checkout/exito?error=1")

        resultado = webpay_client.confirmar_transaccion(token)
        orden = pago.orden

        if resultado.get("status") == "AUTHORIZED":
            pago.estado = EstadoPago.APROBADO
            orden.estado = EstadoOrden.PAGO_CONFIRMADO
            orden.save()
        else:
            pago.estado = EstadoPago.RECHAZADO
        pago.metodo = "webpay_plus"
        pago.save()

        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/checkout/exito?orden={orden.numero}")


class AnalistaPagosListView(APIView):
    permission_classes = [IsRole(RolUsuario.ANALISTA_FINANZAS, RolUsuario.ADMINISTRADOR)]

    def get(self, request):
        return Response(PagoSerializer(Pago.objects.all(), many=True).data)


class AuditarPagoView(APIView):
    permission_classes = [IsRole(RolUsuario.ANALISTA_FINANZAS, RolUsuario.ADMINISTRADOR)]

    def post(self, request, pago_id):
        pago = get_object_or_404(Pago, id=pago_id)
        serializer = AuditoriaPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pago.estado = serializer.validated_data["estado"]
        pago.auditado_por = request.user
        pago.auditado_en = timezone.now()
        pago.save()

        return Response(PagoSerializer(pago).data)
