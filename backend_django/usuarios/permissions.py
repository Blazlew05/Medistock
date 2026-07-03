from rest_framework.permissions import BasePermission


def IsRole(*roles):
    """Factory de permiso DRF que restringe el acceso a los roles indicados."""
    valores_permitidos = {r.value if hasattr(r, "value") else r for r in roles}

    class _IsRole(BasePermission):
        message = f"Acceso denegado. Roles permitidos: {sorted(valores_permitidos)}"

        def has_permission(self, request, view):
            usuario = request.user
            return bool(
                usuario
                and usuario.is_authenticated
                and usuario.rol in valores_permitidos
            )

    return _IsRole
