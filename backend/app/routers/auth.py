"""Router de autenticacion."""
from fastapi import APIRouter, status

from backend.app.core.security import create_access_token
from backend.app.routers.deps import DbSession, UsuarioAutenticado
from backend.app.schemas import TokenResponse, UsuarioCreate, UsuarioLogin, UsuarioRead
from backend.app.services import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticacion"])


@router.post("/registro", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def registrar(datos: UsuarioCreate, db: DbSession):
    """Registra un nuevo usuario. Cualquier rol puede ser creado vía API en este MVP."""
    return AuthService(db).registrar(datos)


@router.post("/login", response_model=TokenResponse)
def login(datos: UsuarioLogin, db: DbSession):
    """Login con email + password. Retorna JWT y datos del usuario."""
    usuario = AuthService(db).autenticar(datos.email, datos.password)
    token = create_access_token({"sub": str(usuario.id), "rol": usuario.rol})
    return TokenResponse(access_token=token, usuario=UsuarioRead.model_validate(usuario))


@router.get("/yo", response_model=UsuarioRead)
def perfil_actual(usuario: UsuarioAutenticado):
    """Devuelve el usuario logueado segun el JWT."""
    return usuario
