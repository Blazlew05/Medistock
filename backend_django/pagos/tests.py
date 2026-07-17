"""Pruebas unitarias — Componentes 7 y 8 del backend MEDISTOCK.

Componente 7: Modelo de Pagos y Auditoría              -> CP-FIN-01/02/03
Componente 8: Flujo de Pago y Control de Acceso        -> CP-INST-02, CP-MP-02/03

Las integraciones externas (MercadoPago / Transbank) se mockean para no depender de la red.

Ejecutar:  python manage.py test pagos --settings=medistock_core.test_settings
"""
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from ordenes import services
from ordenes.models import EstadoOrden, Orden
from productos.models import Bodega, Producto, StockBodega
from usuarios.authentication import create_access_token
from usuarios.models import RolUsuario, Usuario

from .models import EstadoPago, Gateway, Pago


def crear_usuario(email, rol):
    return Usuario.objects.create_user(email=email, password="secret123",
                                       nombre=email, rol=rol)


def make_producto(codigo="P-1", precio=1000, stock=50):
    p = Producto.objects.create(codigo=codigo, nombre=f"Prod {codigo}",
                                categoria="Material", precio=Decimal(precio))
    b = Bodega.objects.create(codigo=f"B-{codigo}", nombre="Bod", region="RM", direccion="x")
    StockBodega.objects.create(producto=p, bodega=b, cantidad=stock)
    return p


def api_as(usuario):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Bearer " + create_access_token(usuario))
    return c


def orden_de(cliente, producto):
    return services.crear_orden(cliente, [{"producto_id": producto.id, "cantidad": 1}],
                                "normal", "media", "dir")


# =================== Componente 7: Modelo Pagos / Auditoría ===================
class PagoModeloAuditoriaTests(TestCase):
    def setUp(self):
        self.paciente = crear_usuario("pac@test.cl", RolUsuario.CLIENTE_PACIENTE)
        self.analista = crear_usuario("ana@test.cl", RolUsuario.ANALISTA_FINANZAS)
        self.orden = orden_de(self.paciente, make_producto("MED-001"))

    def _pago(self):
        return Pago.objects.create(orden=self.orden, monto=self.orden.total)

    def test_estado_por_defecto_pendiente(self):
        self.assertEqual(self._pago().estado, EstadoPago.PENDIENTE)

    def test_gateway_por_defecto_mercadopago(self):
        self.assertEqual(self._pago().gateway, Gateway.MERCADOPAGO)

    def test_str_contiene_numero_orden(self):
        self.assertIn(self.orden.numero, str(self._pago()))

    def test_auditar_aprobado_registra_auditor(self):  # CP-FIN-02
        pago = self._pago()
        resp = api_as(self.analista).post(f"/api/v1/analista/pagos/{pago.id}/auditar",
                                          {"estado": "aprobado"}, format="json")
        self.assertEqual(resp.status_code, 200)
        pago.refresh_from_db()
        self.assertEqual(pago.estado, EstadoPago.APROBADO)
        self.assertEqual(pago.auditado_por_id, self.analista.id)
        self.assertIsNotNone(pago.auditado_en)

    def test_auditar_rechazado_actualiza_estado(self):  # CP-FIN-03
        pago = self._pago()
        resp = api_as(self.analista).post(f"/api/v1/analista/pagos/{pago.id}/auditar",
                                          {"estado": "rechazado"}, format="json")
        self.assertEqual(resp.status_code, 200)
        pago.refresh_from_db()
        self.assertEqual(pago.estado, EstadoPago.RECHAZADO)

    def test_monto_y_relacion_orden(self):
        pago = self._pago()
        self.assertEqual(pago.orden_id, self.orden.id)
        self.assertEqual(int(pago.monto), int(self.orden.total))


# =================== Componente 8: Flujo de Pago y Accesos ===================
class PagoFlujoAccesoTests(TestCase):
    def setUp(self):
        self.paciente = crear_usuario("pac@test.cl", RolUsuario.CLIENTE_PACIENTE)
        self.paciente2 = crear_usuario("pac2@test.cl", RolUsuario.CLIENTE_PACIENTE)
        self.institucion = crear_usuario("inst@test.cl", RolUsuario.CLIENTE_INSTITUCION)
        self.analista = crear_usuario("ana@test.cl", RolUsuario.ANALISTA_FINANZAS)
        self.producto = make_producto("MED-001")

    def test_pago_institucion_no_aprobada_retorna_400(self):  # CP-INST-02
        orden = orden_de(self.institucion, self.producto)  # aprobada_por_ejecutivo = False
        resp = api_as(self.institucion).post(f"/api/v1/pagos/iniciar/{orden.id}")
        self.assertEqual(resp.status_code, 400)

    def test_pago_de_orden_ajena_retorna_403(self):  # CP-MP-03
        orden = orden_de(self.paciente, self.producto)  # aprobada (B2C)
        resp = api_as(self.paciente2).post(f"/api/v1/pagos/iniciar/{orden.id}")
        self.assertEqual(resp.status_code, 403)

    @patch("pagos.views.webpay_client")
    def test_webpay_iniciar_crea_pago(self, mock_webpay):
        mock_webpay.crear_transaccion.return_value = {"token": "TK", "url": "http://wp"}
        orden = orden_de(self.paciente, self.producto)
        resp = api_as(self.paciente).post(f"/api/v1/pagos/webpay/iniciar/{orden.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["token"], "TK")
        self.assertTrue(Pago.objects.filter(orden=orden, gateway=Gateway.WEBPAY).exists())

    def test_analista_lista_pagos(self):  # CP-FIN-01
        orden = orden_de(self.paciente, self.producto)
        Pago.objects.create(orden=orden, monto=orden.total)
        resp = api_as(self.analista).get("/api/v1/analista/pagos")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_cliente_no_accede_a_pagos_analista(self):
        resp = api_as(self.paciente).get("/api/v1/analista/pagos")
        self.assertEqual(resp.status_code, 403)

    @patch("pagos.views.mp_client")
    def test_webhook_aprobado_confirma_orden(self, mock_mp):  # CP-MP-02
        orden = orden_de(self.paciente, self.producto)
        Pago.objects.create(orden=orden, gateway=Gateway.MERCADOPAGO,
                            preference_id="PREF123", monto=orden.total)
        mock_mp.consultar_pago.return_value = {
            "external_reference": orden.numero, "id": "PAY1",
            "payment_method_id": "visa", "status": "approved",
        }
        resp = APIClient().post("/api/v1/pagos/webhook?topic=payment",
                                {"data": {"id": "PAY1"}, "type": "payment"}, format="json")
        self.assertEqual(resp.status_code, 200)
        orden.refresh_from_db()
        self.assertEqual(orden.estado, EstadoOrden.PAGO_CONFIRMADO)
