from django.urls import path

from . import views

urlpatterns = [
    path("productos", views.ProductoListPublicoView.as_view(), name="productos-publico"),
    path("productos/categorias", views.CategoriasView.as_view(), name="productos-categorias"),
    path("productos/<str:codigo>", views.ProductoDetalleView.as_view(), name="productos-detalle"),
    path("admin/productos", views.ProductoAdminListView.as_view(), name="admin-productos"),
    path("admin/productos/<int:producto_id>", views.ProductoAdminDetalleView.as_view(), name="admin-productos-detalle"),
    path("admin/bodegas", views.BodegaListView.as_view(), name="admin-bodegas"),
    path("ejecutivo/productos/<int:producto_id>/stock", views.ProductoStockView.as_view(), name="ejecutivo-producto-stock"),
]
