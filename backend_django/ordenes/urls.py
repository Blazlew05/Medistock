from django.urls import path

from . import views

urlpatterns = [
    path("ordenes", views.OrdenCreateListView.as_view(), name="ordenes-crear"),
    path("ordenes/mis", views.MisOrdenesView.as_view(), name="ordenes-mis"),
    path("ordenes/<int:orden_id>", views.OrdenDetalleView.as_view(), name="ordenes-detalle"),
    path("ejecutivo/ordenes/pendientes", views.OrdenesPendientesAprobacionView.as_view(), name="ejecutivo-ordenes-pendientes"),
    path("ejecutivo/ordenes/<int:orden_id>/aprobar", views.AprobarOrdenView.as_view(), name="ejecutivo-ordenes-aprobar"),
    path("operador/ordenes/priorizadas", views.OrdenesPriorizadasView.as_view(), name="operador-ordenes-priorizadas"),
    path("operador/ordenes/<int:orden_id>/preparar", views.PrepararOrdenView.as_view(), name="operador-ordenes-preparar"),
    path("operador/ordenes/<int:orden_id>/despachar", views.DespacharOrdenView.as_view(), name="operador-ordenes-despachar"),
    path("operador/ordenes/<int:orden_id>/entregar", views.EntregarOrdenView.as_view(), name="operador-ordenes-entregar"),
    path("admin/ordenes", views.AdminOrdenesView.as_view(), name="admin-ordenes"),
    path("admin/dashboard", views.DashboardView.as_view(), name="admin-dashboard"),
]
