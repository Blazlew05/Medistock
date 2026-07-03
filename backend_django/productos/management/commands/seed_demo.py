"""Carga datos de demo: 5 bodegas, 6 usuarios de los 6 roles y 25 productos con stock.

Uso:
    python manage.py seed_demo
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from productos.models import Bodega, Producto, StockBodega
from usuarios.models import RolUsuario, Usuario

BODEGAS = [
    dict(codigo="BOD-001", nombre="Centro Providencia", region="Región Metropolitana",
         direccion="Av. Providencia 1234, Providencia"),
    dict(codigo="BOD-002", nombre="Centro Maipú", region="Región Metropolitana",
         direccion="Av. Pajaritos 5678, Maipú"),
    dict(codigo="BOD-003", nombre="Centro Quilicura", region="Región Metropolitana",
         direccion="Av. Matta 910, Quilicura"),
    dict(codigo="BOD-004", nombre="Centro Concepción", region="Región del Biobío",
         direccion="O'Higgins 234, Concepción"),
    dict(codigo="BOD-005", nombre="Centro Temuco", region="Región de La Araucanía",
         direccion="Caupolicán 567, Temuco"),
]

USUARIOS = [
    dict(email="admin@medistock.cl", password="admin123", nombre="Carolina Soto",
         rol=RolUsuario.ADMINISTRADOR, empresa="MEDISTOCK"),
    dict(email="ejecutivo@medistock.cl", password="ejec123", nombre="Marco Vergara",
         rol=RolUsuario.EJECUTIVO, empresa="MEDISTOCK"),
    dict(email="operador@medistock.cl", password="oper123", nombre="Felipe Reyes",
         rol=RolUsuario.OPERADOR_LOGISTICO, empresa="MEDISTOCK"),
    dict(email="analista@medistock.cl", password="anal123", nombre="Daniela Pinto",
         rol=RolUsuario.ANALISTA_FINANZAS, empresa="MEDISTOCK"),
    dict(email="compras@clinicalasandes.cl", password="clinica123", nombre="Roberto Díaz",
         rol=RolUsuario.CLIENTE_INSTITUCION, empresa="Clínica Las Andes", rut="76.123.456-7",
         direccion="Av. Las Condes 9876, Las Condes"),
    dict(email="paciente@gmail.com", password="paciente123", nombre="Sofía Muñoz",
         rol=RolUsuario.CLIENTE_PACIENTE, rut="15.678.901-2", direccion="Los Leones 432, Providencia"),
]

# (codigo, nombre, descripcion, categoria, precio, unidad, es_critico, requiere_receta)
PRODUCTOS = [
    ("MED-JER-001", "Jeringa desechable 5ml", "Jeringa estéril descartable 5ml con aguja 21G", "Material Descartable", 350, "unidad", False, False),
    ("MED-JER-002", "Jeringa desechable 10ml", "Jeringa estéril descartable 10ml con aguja 21G", "Material Descartable", 450, "unidad", False, False),
    ("MED-GUA-001", "Guantes nitrilo talla M (100u)", "Caja 100 guantes de nitrilo sin polvo talla M", "Material Descartable", 8990, "caja", False, False),
    ("MED-GUA-002", "Guantes nitrilo talla L (100u)", "Caja 100 guantes de nitrilo sin polvo talla L", "Material Descartable", 8990, "caja", False, False),
    ("MED-MAS-001", "Mascarillas quirúrgicas (50u)", "Caja 50 mascarillas quirúrgicas tres pliegues", "Material Descartable", 4990, "caja", False, False),
    ("MED-MAS-002", "Mascarillas KN95 (10u)", "Pack 10 mascarillas KN95 certificadas", "Material Descartable", 6990, "pack", False, False),
    ("MED-GAS-001", "Gasa estéril 10x10cm (100u)", "Caja 100 gasas estériles 10x10 cm", "Material Descartable", 12990, "caja", False, False),
    ("MED-VEN-001", "Venda elástica 10cm", "Venda elástica adhesiva 10cm x 4.5m", "Material Descartable", 2490, "unidad", False, False),

    ("MED-MON-001", "Monitor signos vitales", "Monitor multiparamétrico 5 canales con pantalla 10''", "Equipamiento", 890000, "unidad", True, False),
    ("MED-OXI-001", "Oxímetro de pulso", "Oxímetro de pulso digital portátil", "Equipamiento", 24990, "unidad", True, False),
    ("MED-PRE-001", "Tensiómetro digital", "Tensiómetro digital de brazo automático", "Equipamiento", 39990, "unidad", False, False),
    ("MED-TER-001", "Termómetro infrarrojo", "Termómetro infrarrojo sin contacto", "Equipamiento", 14990, "unidad", False, False),
    ("MED-NEB-001", "Nebulizador portátil", "Nebulizador ultrasónico portátil con accesorios", "Equipamiento", 49990, "unidad", False, False),

    ("MED-SUE-001", "Suero fisiológico 500ml", "Cloruro de sodio 0.9% bolsa 500ml", "Soluciones", 1990, "bolsa", True, False),
    ("MED-SUE-002", "Suero glucosado 5% 500ml", "Solución de glucosa 5% bolsa 500ml", "Soluciones", 2290, "bolsa", True, False),
    ("MED-ALC-001", "Alcohol etílico 70% 1L", "Alcohol etílico antiséptico 70% botella 1L", "Soluciones", 3490, "botella", False, False),
    ("MED-POV-001", "Povidona yodada 120ml", "Solución antiséptica povidona yodada 120ml", "Soluciones", 4490, "frasco", False, False),

    ("MED-PAR-001", "Paracetamol 500mg (20 tab)", "Caja 20 tabletas de paracetamol 500mg", "Fármacos", 1990, "caja", False, False),
    ("MED-IBU-001", "Ibuprofeno 400mg (20 tab)", "Caja 20 tabletas de ibuprofeno 400mg", "Fármacos", 2490, "caja", False, False),
    ("MED-AMO-001", "Amoxicilina 500mg (12 cap)", "Caja 12 cápsulas amoxicilina 500mg", "Fármacos", 5990, "caja", False, True),
    ("MED-OMP-001", "Omeprazol 20mg (14 cap)", "Caja 14 cápsulas omeprazol 20mg", "Fármacos", 3490, "caja", False, False),

    ("MED-CAT-001", "Catéter venoso periférico 20G", "Catéter venoso periférico calibre 20G", "Procedimientos", 1290, "unidad", True, False),
    ("MED-SON-001", "Sonda Foley N16", "Sonda Foley silicona 2 vías N16", "Procedimientos", 2990, "unidad", True, False),
    ("MED-BIS-001", "Bisturí N11 (10u)", "Caja 10 hojas de bisturí estériles N11", "Procedimientos", 3990, "caja", False, False),
    ("MED-SUT-001", "Sutura seda 2/0 c/aguja", "Sutura seda trenzada 2/0 con aguja", "Procedimientos", 1890, "unidad", False, False),
]


class Command(BaseCommand):
    help = "Carga datos de demo (bodegas, usuarios de los 6 roles, productos y stock)"

    def handle(self, *args, **options):
        if Producto.objects.exists():
            self.stdout.write("La BD ya contiene datos. Saltando seed.")
            return

        self.stdout.write("Cargando datos de prueba...")

        bodegas = [Bodega.objects.create(**data) for data in BODEGAS]
        self.stdout.write(f"  {len(bodegas)} bodegas cargadas")

        for data in USUARIOS:
            password = data.pop("password")
            Usuario.objects.create_user(password=password, **data)
        self.stdout.write(f"  {len(USUARIOS)} usuarios cargados")

        productos = []
        for codigo, nombre, desc, categoria, precio, unidad, critico, receta in PRODUCTOS:
            productos.append(Producto.objects.create(
                codigo=codigo, nombre=nombre, descripcion=desc, categoria=categoria,
                precio=Decimal(precio), unidad=unidad, es_critico=critico, requiere_receta=receta,
            ))
        self.stdout.write(f"  {len(productos)} productos cargados")

        stocks = []
        for i, producto in enumerate(productos):
            cantidades = [
                50 + (i * 7) % 100, 30 + (i * 11) % 80, 20 + (i * 13) % 60,
                15 + (i * 17) % 40, 10 + (i * 19) % 30,
            ]
            for bodega, cantidad in zip(bodegas, cantidades):
                stocks.append(StockBodega(
                    producto=producto, bodega=bodega, cantidad=cantidad,
                    lote=f"L-{producto.codigo[-3:]}-{bodega.codigo[-1]}",
                ))
        StockBodega.objects.bulk_create(stocks)
        self.stdout.write(f"  {len(stocks)} registros de stock cargados")

        self.stdout.write(self.style.SUCCESS("\nSeed completado.\n"))
        self.stdout.write("Usuarios de prueba (password mostrado):")
        for data in USUARIOS:
            self.stdout.write(f"  {data['email']}")
