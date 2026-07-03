from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import create_access_token
from .models import Usuario
from .serializers import LoginSerializer, RegistroSerializer, UsuarioSerializer


class RegistroView(APIView):
    """Registra un nuevo usuario. Cualquier rol puede ser creado vía API en este MVP."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Login con email + password. Retorna JWT y datos del usuario."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        usuario = Usuario.objects.filter(email__iexact=email).first()
        if not usuario or not usuario.check_password(password) or not usuario.is_active:
            return Response({"detail": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

        token = create_access_token(usuario)
        return Response({
            "access_token": token,
            "token_type": "bearer",
            "usuario": UsuarioSerializer(usuario).data,
        })


class YoView(APIView):
    """Devuelve el usuario logueado según el JWT."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)
