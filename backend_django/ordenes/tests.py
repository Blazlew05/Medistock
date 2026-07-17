"""Pruebas unitarias — Componentes 5 y 6 del backend MEDISTOCK.

Componente 5: Servicio de Órdenes (lógica de negocio)  -> CP-CLI-03/04, CP-INST-01, CP-OP-03
Componente 6: API de Órdenes y flujo por roles         -> CP-CLI-04, CP-INST-03, CP-OP-01/02

Ejecutar:  python manage.py test ordenes --settings=medistock_core.test_settings
"""
from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from productos.models import Bodega, Producto, StockBodega
from usuarios.authentication import create_access_token
from usuarios.models import RolUsuario, Usuario

from . import services
from .models import EstadoOrden, Orden


def crear_usuario(email, rol):
    return Usuario.objects.create_user(email=email, password="secret123",
                                       nombre=email, rol=rol)


def make_producto(codigo="P-1", precio=1000, stock=10):
    p = Producto.objects.create(codigo=codigo, nombre=f"Prod {codigo}",
                                categoria="Material", precio=Decimal(precio))
    b = Bodega.objects.create(codigo=f"B-{codigo}", nombre="Bod", region="RM", direccion="x")
    StockBodega.objects.create(producto=p, bodega=b, cantidad=stock)
    return p


def api_as(usuario):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Bearer " + create_access_token(usuario))
    return c


# =================== Componente 5: Servicio de Órdenes ===================
class OrdenServiceTests(TestCase):
    def setUp(self):
        self.paciente = crear_usuario("pac@test.cl", RolUsuario.CLIENTE_PACIENTE)
        self.institucion = crear_usuario("inst@test.cl", RolUsuario.CLIENTE_INSTITUCION)
        self.producto = make_producto("MED-001", precio=1000, stock=10)

    def _items(self, cantidad=2):
        return [{"producto_id": self.producto.id, "cantidad": cantidad}]

    def test_orden_paciente_queda_autoaprobada(self):  # CP-CLI-04
        orden = services.crear_orden(self.paciente, self._items(), "normal", "media", "dir")
        self.assertTrue(orden.aprobada_por_ejecutivo)

    def test_orden_institucion_requiere_aprobacion(self):  # CP-INST-01
        orden = services.crear_orden(self.institucion, self._items(), "normal", "media", "dir")
        self.assertFalse(orden.aprobada_por_ejecutivo)

    def test_stock_insuficiente_lanza_error(self):  # CP-CLI-03
        with self.assertRaises(ValidationError):
            services.crear_orden(self.paciente, self._items(cantidad=999), "normal", "media", "dir")

    def test_calcula_costo_envio_y_total(self):
        orden_exp = services.crear_orden(self.paciente, self._items(2), "express", "media", "dir")
        self.assertEqual(int(orden_exp.costo_envio), 5990)
        self.assertEqual(int(orden_exp.total), int(orden_exp.subtotal) + 5990)
        orden_nor = services.crear_orden(self.paciente, self._items(1), "normal", "media", "dir")
        self.assertEqual(int(orden_nor.costo_envio), 2990)

    def test_numero_orden_tiene_prefijo(self):
        orden = services.crear_orden(self.paciente, self._items(), "normal", "media", "dir")
        self.assertTrue(orden.numero.startswith("OC-"))

    def test_despachar_genera_tracking(self):  # CP-OP-03
        orden = services.crear_orden(self.paciente, self._items(), "normal", "media", "dir")
        services.cambiar_estado(orden, EstadoOrden.DESPACHADO)
        self.assertEqual(orden.estado, EstadoOrden.DESPACHADO)
        self.assertTrue(orden.tracking_simulado.startswith("MED-"))


# =================== Componente 6: API de Órdenes por rol ===================
class OrdenAPITests(TestCase):
    def setUp(self):
        self.paciente = crear_usuario("pac@test.cl", RolUsuario.CLIENTE_PACIENTE)
        self.institucion = crear_usuario("inst@test.cl", RolUsuario.CLIENTE_INSTITUCION)
        self.ejecutivo = crear_usuario("eje@test.cl", RolUsuario.EJECUTIVO)
        self.operador = crear_usuario("ope@test.cl", RolUsuario.OPERADOR_LOGISTICO)
        self.producto = make_producto("MED-001", precio=1000, stock=100)

    def _payload(self, cantidad=1, urgencia="media"):
        return {"items": [{"producto_id": self.producto.id, "cantidad": cantidad}],
                "tipo_despacho": "normal", "urgencia": urgencia, "direccion_envio": "dir"}

    def test_crear_orden_retorna_201(self):  # CP-CLI-04
        resp = api_as(self.paciente).post("/api/v1/ordenes", self._payload(), format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data["aprobada_por_ejecutivo"])

    def test_mis_ordenes_solo_propias(self):
        services.crear_orden(self.paciente, [{"producto_id": self.producto.id, "cantidad": 1}],
                             "normal", "media", "dir")
        resp = api_as(self.institucion).get("/api/v1/ordenes/mis")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)  # la institución no ve la orden del paciente

    def test_ejecutivo_aprueba_orden(self):  # CP-INST-03
        orden = services.crear_orden(self.institucion,
                                     [{"producto_id": self.producto.id, "cantidad": 1}],
                                     "normal", "media", "dir")
        resp = api_as(self.ejecutivo).post(f"/api/v1/ejecutivo/ordenes/{orden.id}/aprobar")
        self.assertEqual(resp.status_code, 200)
        orden.refresh_from_db()
        self.assertTrue(orden.aprobada_por_ejecutivo)

    def test_priorizadas_urgencia_alta_primero(self):  # CP-OP-01
        baja = services.crear_orden(self.paciente, [{"producto_id": self.producto.id, "cantidad": 1}],
                                    "normal", "baja", "dir")
        alta = services.crear_orden(self.paciente, [{"producto_id": self.producto.id, "cantidad": 1}],
                                    "normal", "alta", "dir")
        for o in (baja, alta):
            services.cambiar_estado(o, EstadoOrden.PAGO_CONFIRMADO)
        resp = api_as(self.operador).get("/api/v1/operador/ordenes/priorizadas")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]["urgencia"], "alta")

    def test_operador_prepara_orden(self):  # CP-OP-02
        orden = services.crear_orden(self.paciente, [{"producto_id": self.producto.id, "cantidad": 1}],
                                     "normal", "media", "dir")
        services.cambiar_estado(orden, EstadoOrden.PAGO_CONFIRMADO)
        resp = api_as(self.operador).post(f"/api/v1/operador/ordenes/{orden.id}/preparar")
        self.assertEqual(resp.status_code, 200)
        orden.refresh_from_db()
        self.assertEqual(orden.estado, EstadoOrden.EN_PREPARACION)

    def test_cliente_no_ve_orden_ajena(self):
        orden = services.crear_orden(self.paciente, [{"producto_id": self.producto.id, "cantidad": 1}],
                                     "normal", "media", "dir")
        resp = api_as(self.institucion).get(f"/api/v1/ordenes/{orden.id}")
        self.assertEqual(resp.status_code, 403)
