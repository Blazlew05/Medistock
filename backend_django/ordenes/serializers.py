from rest_framework import serializers

from .models import ItemOrden, Orden, TipoDespacho, Urgencia


class ItemOrdenCreateSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)


class ItemOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemOrden
        fields = ["id", "producto_id", "nombre_producto", "cantidad", "precio_unitario", "subtotal"]


class OrdenCreateSerializer(serializers.Serializer):
    items = ItemOrdenCreateSerializer(many=True)
    tipo_despacho = serializers.ChoiceField(choices=TipoDespacho.choices, default=TipoDespacho.NORMAL)
    urgencia = serializers.ChoiceField(choices=Urgencia.choices, default=Urgencia.MEDIA)
    direccion_envio = serializers.CharField()
    notas = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class OrdenSerializer(serializers.ModelSerializer):
    items = ItemOrdenSerializer(many=True, read_only=True)
    cliente_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Orden
        fields = [
            "id", "numero", "cliente_id", "estado", "urgencia", "tipo_despacho", "direccion_envio",
            "subtotal", "costo_envio", "total", "notas", "aprobada_por_ejecutivo",
            "tracking_simulado", "creada_en", "items",
        ]


class OrdenListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orden
        fields = ["id", "numero", "estado", "urgencia", "tipo_despacho", "total", "creada_en"]
