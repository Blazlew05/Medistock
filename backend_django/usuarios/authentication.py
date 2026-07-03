from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Usuario


def create_access_token(usuario):
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(usuario.id), "rol": usuario.rol, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith(f"{self.keyword} "):
            return None

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.PyJWTError:
            raise AuthenticationFailed("Token inválido o expirado")

        usuario_id = payload.get("sub")
        if not usuario_id:
            raise AuthenticationFailed("Token mal formado")

        try:
            usuario = Usuario.objects.get(pk=int(usuario_id))
        except Usuario.DoesNotExist:
            raise AuthenticationFailed("Usuario no encontrado")

        if not usuario.is_active:
            raise AuthenticationFailed("Usuario no encontrado")

        return (usuario, token)

    def authenticate_header(self, request):
        return self.keyword
