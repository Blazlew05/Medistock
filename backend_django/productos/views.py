from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import RolUsuario
from usuarios.permissions import IsRole

from .models import Bodega, Producto
from .serializers import BodegaSerializer, ProductoConStockSerializer, ProductoSerializer


class ProductoListPublicoView(APIView):
    """Listado público de productos activos. Consumido también por ERPs externos (Cruz Amarilla)."""

    permission_classes = [AllowAny]

    def get(self, request):
        productos = Producto.objects.filter(activo=True)
        categoria = request.query_params.get("categoria")
        if categoria:
            productos = productos.filter(categoria=categoria)
        return Response(ProductoSerializer(productos, many=True).data)


class CategoriasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categorias = (
            Producto.objects.filter(activo=True)
            .order_by("categoria")
            .values_list("categoria", flat=True)
            .distinct()
        )
        return Response(list(categorias))


class ProductoDetalleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, codigo):
        producto = get_object_or_404(Producto, codigo=codigo)
        return Response(ProductoSerializer(producto).data)


class ProductoAdminListView(APIView):
    permission_classes = [IsRole(RolUsuario.ADMINISTRADOR)]

    def get(self, request):
        return Response(ProductoSerializer(Producto.objects.all(), many=True).data)

    def post(self, request):
        serializer = ProductoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto = serializer.save()
        return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)


class ProductoAdminDetalleView(APIView):
    permission_classes = [IsRole(RolUsuario.ADMINISTRADOR)]

    def put(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        serializer = ProductoSerializer(producto, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProductoStockView(APIView):
    permission_classes = [IsRole(RolUsuario.EJECUTIVO, RolUsuario.ADMINISTRADOR)]

    def get(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        return Response(ProductoConStockSerializer(producto).data)


class BodegaListView(APIView):
    permission_classes = [IsRole(RolUsuario.ADMINISTRADOR, RolUsuario.EJECUTIVO, RolUsuario.OPERADOR_LOGISTICO)]

    def get(self, request):
        return Response(BodegaSerializer(Bodega.objects.all(), many=True).data)
