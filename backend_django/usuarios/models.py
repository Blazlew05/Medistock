from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class RolUsuario(models.TextChoices):
    CLIENTE_INSTITUCION = "cliente_institucion", "Cliente institución"
    CLIENTE_PACIENTE = "cliente_paciente", "Cliente paciente"
    ADMINISTRADOR = "administrador", "Administrador"
    EJECUTIVO = "ejecutivo", "Ejecutivo"
    OPERADOR_LOGISTICO = "operador_logistico", "Operador logístico"
    ANALISTA_FINANZAS = "analista_finanzas", "Analista de finanzas"


ROLES_INTERNOS = {
    RolUsuario.ADMINISTRADOR,
    RolUsuario.EJECUTIVO,
    RolUsuario.OPERADOR_LOGISTICO,
    RolUsuario.ANALISTA_FINANZAS,
}

ROLES_CLIENTE = {
    RolUsuario.CLIENTE_INSTITUCION,
    RolUsuario.CLIENTE_PACIENTE,
}


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", RolUsuario.ADMINISTRADOR)
        extra_fields.setdefault("nombre", email)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=255)
    rol = models.CharField(max_length=30, choices=RolUsuario.choices)
    empresa = models.CharField(max_length=255, blank=True, null=True)
    rut = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre", "rol"]

    objects = UsuarioManager()

    def __str__(self):
        return self.email
