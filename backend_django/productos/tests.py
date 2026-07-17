"""Pruebas unitarias — Componentes 3 y 4 del backend MEDISTOCK.

Componente 3: Modelo de Productos / Stock (Producto, Bodega, StockBodega)
Componente 4: API Pública de Catálogo                 -> CP-API-01..05

Ejecutar:  python manage.py test productos --settings=medistock_core.test_settings
"""
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Bodega, Producto, StockBodega
from .serializers import ProductoSerializer


def make_producto(codigo="P-1", precio=1000, stock=10, categoria="Material", activo=True):
    p = Producto.objects.create(
        codigo=codigo, nombre=f"Producto {codigo}", descripcion="desc",
        categoria=categoria, precio=Decimal(precio), activo=activo,
    )
    if stock:
        b = Bodega.objects.create(codigo=f"B-{codigo}", nombre="Bodega",
                                  region="RM", direccion="Calle 1")
        StockBodega.objects.create(producto=p, bodega=b, cantidad=stock)
    return p


# =================== Componente 3: Modelo Productos / Stock ===================
class ProductoModeloTests(TestCase):
    def test_crear_producto_y_str(self):
        p = make_producto("MED-001", precio=350, stock=0)
        self.assertEqual(str(p), "MED-001 - Producto MED-001")

    def test_stock_total_suma_bodegas(self):
        p = make_producto("MED-002", stock=0)
        b1 = Bodega.objects.create(codigo="BX1", nombre="B1", region="RM", direccion="x")
        b2 = Bodega.objects.create(codigo="BX2", nombre="B2", region="RM", direccion="y")
        StockBodega.objects.create(producto=p, bodega=b1, cantidad=30)
        StockBodega.objects.create(producto=p, bodega=b2, cantidad=20)
        self.assertEqual(p.stock_total, 50)

    def test_stock_total_cero_sin_registros(self):
        p = make_producto("MED-003", stock=0)
        self.assertEqual(p.stock_total, 0)

    def test_codigo_es_unico(self):
        make_producto("MED-DUP", stock=0)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_producto("MED-DUP", stock=0)

    def test_producto_activo_por_defecto(self):
        p = make_producto("MED-004", stock=0)
        self.assertTrue(p.activo)

    def test_serializer_incluye_stock_total(self):
        p = make_producto("MED-005", precio=999, stock=7)
        data = ProductoSerializer(p).data
        self.assertEqual(data["stock_total"], 7)
        self.assertEqual(data["codigo"], "MED-005")


# =================== Componente 4: API Pública de Catálogo ===================
class CatalogoAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        make_producto("MED-JER-001", precio=350, stock=50, categoria="Material Descartable")
        make_producto("MED-PAR-001", precio=1990, stock=20, categoria="Fármacos")

    def test_listar_productos_sin_auth_retorna_200(self):  # CP-API-01
        resp = self.client.get("/api/v1/productos")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_filtrar_por_categoria(self):  # CP-API-02
        resp = self.client.get("/api/v1/productos?categoria=Fármacos")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["categoria"], "Fármacos")

    def test_detalle_por_codigo(self):  # CP-API-03
        resp = self.client.get("/api/v1/productos/MED-JER-001")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["codigo"], "MED-JER-001")

    def test_producto_inexistente_retorna_404(self):  # CP-API-04
        resp = self.client.get("/api/v1/productos/NO-EXISTE-999")
        self.assertEqual(resp.status_code, 404)

    def test_categorias_retorna_array_no_vacio(self):  # CP-API-05
        resp = self.client.get("/api/v1/productos/categorias")
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_solo_productos_activos_en_listado(self):
        make_producto("MED-INACTIVO", stock=5, activo=False)
        resp = self.client.get("/api/v1/productos")
        codigos = [p["codigo"] for p in resp.data]
        self.assertNotIn("MED-INACTIVO", codigos)
