"""URL configuration for medistock_core project."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health", health, name="health"),
    path("api/v1/auth/", include("usuarios.urls")),
    path("api/v1/", include("productos.urls")),
    path("api/v1/", include("ordenes.urls")),
    path("api/v1/", include("pagos.urls")),
]
