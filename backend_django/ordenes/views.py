from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import ROLES_INTERNOS, RolUsuario
from usuarios.permissions import IsRole

from . import services
from .models import EstadoOrden, Orden
from .serializers import OrdenCreateSerializer, OrdenListSerializer, OrdenSerializer

_ORDEN_URGENCIA = {"alta": 0, "media": 1, "baja": 2}


class OrdenCreateListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.rol not in (RolUsuario.CLIENTE_PACIENTE, RolUsuario.CLIENTE_INSTITUCION):
            raise PermissionDenied("Solo clientes pueden crear órdenes")

        serializer = OrdenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        orden = services.crear_orden(
            cliente=request.user,
            items_data=data["items"],
            tipo_despacho=data["tipo_despacho"],
            urgencia=data["urgencia"],
            direccion_envio=data["direccion_envio"],
            notas=data.get("notas"),
        )
        return Response(OrdenSerializer(orden).data, status=status.HTTP_201_CREATED)


class MisOrdenesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ordenes = Orden.objects.filter(cliente=request.user)
        return Response(OrdenListSerializer(ordenes, many=True).data)


class OrdenDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, orden_id):
        orden = get_object_or_404(Orden, id=orden_id)
        es_dueno = orden.cliente_id == request.user.id
        if not es_dueno and request.user.rol not in ROLES_INTERNOS:
            raise PermissionDenied("No tienes acceso a esta orden")
        return Response(OrdenSerializer(orden).data)


class OrdenesPendientesAprobacionView(APIView):
    permission_classes = [IsRole(RolUsuario.EJECUTIVO, RolUsuario.ADMINISTRADOR)]

    def get(self, request):
        ordenes = Orden.objects.filter(aprobada_por_ejecutivo=False, estado=EstadoOrden.PENDIENTE_PAGO)
        return Response(OrdenSerializer(ordenes, many=True).data)


class AprobarOrdenView(APIView):
    permission_classes = [IsRole(RolUsuario.EJECUTIVO, RolUsuario.ADMINISTRADOR)]

    def post(self, request, orden_id):
        orden = get_object_or_404(Orden, id=orden_id)
        orden.aprobada_por_ejecutivo = True
        orden.save()
        return Response(OrdenSerializer(orden).data)


class OrdenesPriorizadasView(APIView):
    permission_classes = [IsRole(RolUsuario.OPERADOR_LOGISTICO, RolUsuario.ADMINISTRADOR)]

    def get(self, request):
        ordenes = list(
            Orden.objects.filter(estado__in=[EstadoOrden.PAGO_CONFIRMADO, EstadoOrden.EN_PREPARACION])
        )
        ordenes.sort(key=lambda o: (_ORDEN_URGENCIA[o.urgencia], o.creada_en))
        return Response(OrdenSerializer(ordenes, many=True).data)


class _CambiarEstadoView(APIView):
    permission_classes = [IsRole(RolUsuario.OPERADOR_LOGISTICO, RolUsuario.ADMINISTRADOR)]
    nuevo_estado = None

    def post(self, request, orden_id):
        orden = get_object_or_404(Orden, id=orden_id)
        services.cambiar_estado(orden, self.nuevo_estado)
        return Response(OrdenSerializer(orden).data)


class PrepararOrdenView(_CambiarEstadoView):
    nuevo_estado = EstadoOrden.EN_PREPARACION


class DespacharOrdenView(_CambiarEstadoView):
    nuevo_estado = EstadoOrden.DESPACHADO


class EntregarOrdenView(_CambiarEstadoView):
    nuevo_estado = EstadoOrden.ENTREGADO


class AdminOrdenesView(APIView):
    permission_classes = [IsRole(RolUsuario.ADMINISTRADOR)]

    def get(self, request):
        return Response(OrdenSerializer(Orden.objects.all(), many=True).data)


class DashboardView(APIView):
    permission_classes = [IsRole(RolUsuario.ADMINISTRADOR)]

    def get(self, request):
        from pagos.models import EstadoPago, Pago
        from productos.models import Producto
        from usuarios.models import Usuario

        total_clientes = Usuario.objects.filter(
            rol__in=[RolUsuario.CLIENTE_PACIENTE, RolUsuario.CLIENTE_INSTITUCION]
        ).count()
        pagos_aprobados = Pago.objects.filter(estado=EstadoPago.APROBADO)

        return Response({
            "total_productos": Producto.objects.count(),
            "total_clientes": total_clientes,
            "total_ordenes": Orden.objects.count(),
            "ordenes_pendientes_pago": Orden.objects.filter(estado=EstadoOrden.PENDIENTE_PAGO).count(),
            "ordenes_en_preparacion": Orden.objects.filter(estado=EstadoOrden.EN_PREPARACION).count(),
            "ordenes_despachadas": Orden.objects.filter(estado=EstadoOrden.DESPACHADO).count(),
            "pagos_aprobados": pagos_aprobados.count(),
            "monto_total_aprobado": sum((p.monto for p in pagos_aprobados), 0),
        })
