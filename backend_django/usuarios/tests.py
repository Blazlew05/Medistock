"""Pruebas unitarias — Componentes 1 y 2 del backend MEDISTOCK.

Componente 1: Autenticación (registro / login)      -> CP-AUTH-01..05
Componente 2: JWT y Control de Acceso por rol         -> CP-AUTH-05/06, RNF-03/04

Ejecutar:  python manage.py test usuarios --settings=medistock_core.test_settings
"""
import jwt
from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from .authentication import JWTAuthentication, create_access_token
from .models import RolUsuario, Usuario
from .permissions import IsRole
from .serializers import UsuarioSerializer


def crear_usuario(email, rol, password="secret123", activo=True, **extra):
    u = Usuario.objects.create_user(
        email=email, password=password,
        nombre=extra.pop("nombre", email), rol=rol, **extra,
    )
    if not activo:
        u.is_active = False
        u.save()
    return u


# ===================== Componente 1: Autenticación =====================
class AutenticacionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registro_paciente_exitoso(self):  # CP-AUTH-03
        resp = self.client.post("/api/v1/auth/registro", {
            "nombre": "Juan Pérez", "email": "juan@test.cl",
            "password": "clave123", "rol": RolUsuario.CLIENTE_PACIENTE,
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Usuario.objects.filter(email="juan@test.cl").exists())
        self.assertNotIn("password", resp.data)  # nunca se expone

    def test_registro_email_duplicado_retorna_400(self):  # CP-AUTH-04
        crear_usuario("dup@test.cl", RolUsuario.CLIENTE_PACIENTE)
        resp = self.client.post("/api/v1/auth/registro", {
            "nombre": "Otro", "email": "dup@test.cl",
            "password": "clave123", "rol": RolUsuario.CLIENTE_PACIENTE,
        }, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_login_exitoso_devuelve_token(self):  # CP-AUTH-01
        crear_usuario("admin@test.cl", RolUsuario.ADMINISTRADOR, password="admin123")
        resp = self.client.post("/api/v1/auth/login",
                                {"email": "admin@test.cl", "password": "admin123"},
                                format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access_token", resp.data)
        self.assertEqual(resp.data["usuario"]["rol"], RolUsuario.ADMINISTRADOR)

    def test_login_password_incorrecto_retorna_401(self):  # CP-AUTH-02
        crear_usuario("admin@test.cl", RolUsuario.ADMINISTRADOR, password="admin123")
        resp = self.client.post("/api/v1/auth/login",
                                {"email": "admin@test.cl", "password": "mala"},
                                format="json")
        self.assertEqual(resp.status_code, 401)

    def test_login_usuario_inactivo_retorna_401(self):
        crear_usuario("inact@test.cl", RolUsuario.CLIENTE_PACIENTE,
                      password="clave123", activo=False)
        resp = self.client.post("/api/v1/auth/login",
                                {"email": "inact@test.cl", "password": "clave123"},
                                format="json")
        self.assertEqual(resp.status_code, 401)

    def test_perfil_sin_token_retorna_401(self):  # CP-AUTH-05
        resp = self.client.get("/api/v1/auth/yo")
        self.assertEqual(resp.status_code, 401)


# ================= Componente 2: JWT y Control de Acceso =================
class JWTyControlAccesoTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.usuario = crear_usuario("u@test.cl", RolUsuario.ADMINISTRADOR)

    def test_token_codifica_sub_y_rol(self):
        token = create_access_token(self.usuario)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        self.assertEqual(payload["sub"], str(self.usuario.id))
        self.assertEqual(payload["rol"], RolUsuario.ADMINISTRADOR)

    def test_authentication_valida_token_correcto(self):
        token = create_access_token(self.usuario)
        req = self.factory.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
        user, _ = JWTAuthentication().authenticate(req)
        self.assertEqual(user.id, self.usuario.id)

    def test_authentication_rechaza_token_invalido(self):
        from rest_framework.exceptions import AuthenticationFailed
        req = self.factory.get("/", HTTP_AUTHORIZATION="Bearer token.falso.xxx")
        with self.assertRaises(AuthenticationFailed):
            JWTAuthentication().authenticate(req)

    def test_isrole_permite_rol_correcto(self):  # RNF-04
        req = self.factory.get("/")
        req.user = self.usuario
        permiso = IsRole(RolUsuario.ADMINISTRADOR)()
        self.assertTrue(permiso.has_permission(req, None))

    def test_isrole_bloquea_rol_incorrecto(self):  # CP-AUTH-06
        cliente = crear_usuario("cli@test.cl", RolUsuario.CLIENTE_PACIENTE)
        req = self.factory.get("/")
        req.user = cliente
        permiso = IsRole(RolUsuario.ADMINISTRADOR)()
        self.assertFalse(permiso.has_permission(req, None))

    def test_serializer_no_expone_password(self):  # RNF-03
        data = UsuarioSerializer(self.usuario).data
        self.assertNotIn("password", data)
        self.assertNotIn("password_hash", data)
