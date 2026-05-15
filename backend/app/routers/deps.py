"""Dependencias de FastAPI para autenticacion y autorizacion."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import RolUsuario
from app.core.security import decode_token
from app.models import Usuario
from app.repositories import UsuarioRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_usuario_actual(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    usuario_id = payload.get("sub")
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token mal formado"
        )
    usuario = UsuarioRepository(db).get_by_id(int(usuario_id))
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    return usuario


UsuarioAutenticado = Annotated[Usuario, Depends(get_usuario_actual)]
DbSession = Annotated[Session, Depends(get_db)]


def requiere_roles(*roles_permitidos: RolUsuario):
    """Factory de dependencia para restringir endpoints por rol."""

    def verificar(usuario: UsuarioAutenticado) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles permitidos: {[r.value for r in roles_permitidos]}",
            )
        return usuario

    return verificar
