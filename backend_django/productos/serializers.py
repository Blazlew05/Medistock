from rest_framework import serializers

from .models import Bodega, Producto, StockBodega


class ProductoSerializer(serializers.ModelSerializer):
    stock_total = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            "id", "codigo", "nombre", "descripcion", "categoria", "precio", "unidad",
            "imagen_url", "requiere_receta", "es_critico", "activo", "stock_total", "creado_en",
        ]
        read_only_fields = ["id", "creado_en"]

    def get_stock_total(self, obj):
        return obj.stock_total


class BodegaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bodega
        fields = ["id", "codigo", "nombre", "region", "direccion", "activa"]


class StockPorBodegaSerializer(serializers.ModelSerializer):
    bodega_id = serializers.IntegerField(source="bodega.id")
    bodega_nombre = serializers.CharField(source="bodega.nombre")
    bodega_region = serializers.CharField(source="bodega.region")

    class Meta:
        model = StockBodega
        fields = ["bodega_id", "bodega_nombre", "bodega_region", "cantidad", "lote"]


class ProductoConStockSerializer(ProductoSerializer):
    stock_por_bodega = serializers.SerializerMethodField()

    class Meta(ProductoSerializer.Meta):
        fields = ProductoSerializer.Meta.fields + ["stock_por_bodega"]

    def get_stock_por_bodega(self, obj):
        stocks = obj.stocks.select_related("bodega").all()
        return StockPorBodegaSerializer(stocks, many=True).data
