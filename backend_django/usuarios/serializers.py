from rest_framework import serializers

from .models import RolUsuario, Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    activo = serializers.BooleanField(source="is_active", read_only=True)
    creado_en = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id", "email", "nombre", "rol", "empresa", "rut",
            "telefono", "direccion", "activo", "creado_en",
        ]


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ["email", "nombre", "rol", "empresa", "rut", "telefono", "direccion", "password"]

    def validate_email(self, value):
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("El email ya está registrado")
        return value

    def validate_rol(self, value):
        if value not in RolUsuario.values:
            raise serializers.ValidationError("Rol inválido")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        return Usuario.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
