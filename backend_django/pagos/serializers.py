from rest_framework import serializers

from .models import EstadoPago, Pago


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            "id", "orden_id", "gateway", "mercadopago_id", "preference_id",
            "monto", "estado", "metodo", "auditado_en", "creado_en",
        ]


class AuditoriaPagoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=EstadoPago.choices)
    nota = serializers.CharField(required=False, allow_blank=True, allow_null=True)
