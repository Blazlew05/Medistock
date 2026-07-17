"""Configuración de pruebas: BD SQLite en memoria (no requiere Docker/Postgres).

Uso:
    python manage.py test --settings=medistock_core.test_settings
"""
from medistock_core.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Hasher rápido para acelerar la creación de usuarios en los tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Credenciales sandbox por defecto para las integraciones (los tests las mockean).
MERCADOPAGO_ACCESS_TOKEN = "TEST-token"
