"""Script para inicializar la BD: crea tablas y carga datos de prueba.

Uso:
    python seed.py
"""
from decimal import Decimal

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.core.enums import RolUsuario
from backend.app.core.security import hash_password
from backend.app.models import Bodega, Producto, StockBodega, Usuario


def crear_tablas():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")


def cargar_bodegas(db):
    bodegas = [
        Bodega(codigo="BOD-001", nombre="Centro Providencia", region="Region Metropolitana",
               direccion="Av. Providencia 1234, Providencia"),
        Bodega(codigo="BOD-002", nombre="Centro Maipu", region="Region Metropolitana",
               direccion="Av. Pajaritos 5678, Maipu"),
        Bodega(codigo="BOD-003", nombre="Centro Quilicura", region="Region Metropolitana",
               direccion="Av. Matta 910, Quilicura"),
        Bodega(codigo="BOD-004", nombre="Centro Concepcion", region="Region del Biobio",
               direccion="O'Higgins 234, Concepcion"),
        Bodega(codigo="BOD-005", nombre="Centro Temuco", region="Region de La Araucania",
               direccion="Caupolican 567, Temuco"),
    ]
    db.add_all(bodegas)
    db.commit()
    print(f"  {len(bodegas)} bodegas cargadas")
    return bodegas


def cargar_usuarios(db):
    usuarios = [
        # Admin
        Usuario(email="admin@medistock.cl", password_hash=hash_password("admin123"),
                nombre="Carolina Soto", rol=RolUsuario.ADMINISTRADOR, empresa="MEDISTOCK"),
        # Ejecutivo
        Usuario(email="ejecutivo@medistock.cl", password_hash=hash_password("ejec123"),
                nombre="Marco Vergara", rol=RolUsuario.EJECUTIVO, empresa="MEDISTOCK"),
        # Operador
        Usuario(email="operador@medistock.cl", password_hash=hash_password("oper123"),
                nombre="Felipe Reyes", rol=RolUsuario.OPERADOR_LOGISTICO, empresa="MEDISTOCK"),
        # Analista
        Usuario(email="analista@medistock.cl", password_hash=hash_password("anal123"),
                nombre="Daniela Pinto", rol=RolUsuario.ANALISTA_FINANZAS, empresa="MEDISTOCK"),
        # Cliente institucional
        Usuario(email="compras@clinicalasandes.cl", password_hash=hash_password("clinica123"),
                nombre="Roberto Diaz", rol=RolUsuario.CLIENTE_INSTITUCION,
                empresa="Clinica Las Andes", rut="76.123.456-7",
                direccion="Av. Las Condes 9876, Las Condes"),
        # Cliente paciente
        Usuario(email="paciente@gmail.com", password_hash=hash_password("paciente123"),
                nombre="Sofia Munoz", rol=RolUsuario.CLIENTE_PACIENTE,
                rut="15.678.901-2", direccion="Los Leones 432, Providencia"),
    ]
    db.add_all(usuarios)
    db.commit()
    print(f"  {len(usuarios)} usuarios cargados")


def cargar_productos_y_stock(db, bodegas):
    productos_data = [
        # (codigo, nombre, descripcion, categoria, precio, unidad, critico, receta)
        ("MED-JER-001", "Jeringa desechable 5ml", "Jeringa esteril descartable 5ml con aguja 21G", "Material Descartable", 350, "unidad", False, False),
        ("MED-JER-002", "Jeringa desechable 10ml", "Jeringa esteril descartable 10ml con aguja 21G", "Material Descartable", 450, "unidad", False, False),
        ("MED-GUA-001", "Guantes nitrilo talla M (100u)", "Caja 100 guantes de nitrilo sin polvo talla M", "Material Descartable", 8990, "caja", False, False),
        ("MED-GUA-002", "Guantes nitrilo talla L (100u)", "Caja 100 guantes de nitrilo sin polvo talla L", "Material Descartable", 8990, "caja", False, False),
        ("MED-MAS-001", "Mascarillas quirurgicas (50u)", "Caja 50 mascarillas quirurgicas tres pliegues", "Material Descartable", 4990, "caja", False, False),
        ("MED-MAS-002", "Mascarillas KN95 (10u)", "Pack 10 mascarillas KN95 certificadas", "Material Descartable", 6990, "pack", False, False),
        ("MED-GAS-001", "Gasa esteril 10x10cm (100u)", "Caja 100 gasas estériles 10x10 cm", "Material Descartable", 12990, "caja", False, False),
        ("MED-VEN-001", "Venda elastica 10cm", "Venda elastica adhesiva 10cm x 4.5m", "Material Descartable", 2490, "unidad", False, False),

        ("MED-MON-001", "Monitor signos vitales", "Monitor multiparametrico 5 canales con pantalla 10''", "Equipamiento", 890000, "unidad", True, False),
        ("MED-OXI-001", "Oximetro de pulso", "Oximetro de pulso digital portatil", "Equipamiento", 24990, "unidad", True, False),
        ("MED-PRE-001", "Tensiometro digital", "Tensiometro digital de brazo automatico", "Equipamiento", 39990, "unidad", False, False),
        ("MED-TER-001", "Termometro infrarrojo", "Termometro infrarrojo sin contacto", "Equipamiento", 14990, "unidad", False, False),
        ("MED-NEB-001", "Nebulizador portatil", "Nebulizador ultrasonico portatil con accesorios", "Equipamiento", 49990, "unidad", False, False),

        ("MED-SUE-001", "Suero fisiologico 500ml", "Cloruro de sodio 0.9% bolsa 500ml", "Soluciones", 1990, "bolsa", True, False),
        ("MED-SUE-002", "Suero glucosado 5% 500ml", "Solucion de glucosa 5% bolsa 500ml", "Soluciones", 2290, "bolsa", True, False),
        ("MED-ALC-001", "Alcohol etilico 70% 1L", "Alcohol etilico antiseptico 70% botella 1L", "Soluciones", 3490, "botella", False, False),
        ("MED-POV-001", "Povidona yodada 120ml", "Solucion antiseptica povidona yodada 120ml", "Soluciones", 4490, "frasco", False, False),

        ("MED-PAR-001", "Paracetamol 500mg (20 tab)", "Caja 20 tabletas de paracetamol 500mg", "Farmacos", 1990, "caja", False, False),
        ("MED-IBU-001", "Ibuprofeno 400mg (20 tab)", "Caja 20 tabletas de ibuprofeno 400mg", "Farmacos", 2490, "caja", False, False),
        ("MED-AMO-001", "Amoxicilina 500mg (12 cap)", "Caja 12 capsulas amoxicilina 500mg", "Farmacos", 5990, "caja", False, True),
        ("MED-OMP-001", "Omeprazol 20mg (14 cap)", "Caja 14 capsulas omeprazol 20mg", "Farmacos", 3490, "caja", False, False),

        ("MED-CAT-001", "Cateter venoso periferico 20G", "Cateter venoso periferico calibre 20G", "Procedimientos", 1290, "unidad", True, False),
        ("MED-SON-001", "Sonda Foley N16", "Sonda Foley silicona 2 vias N16", "Procedimientos", 2990, "unidad", True, False),
        ("MED-BIS-001", "Bisturi N11 (10u)", "Caja 10 hojas de bisturi esteriles N11", "Procedimientos", 3990, "caja", False, False),
        ("MED-SUT-001", "Sutura seda 2/0 c/aguja", "Sutura seda trenzada 2/0 con aguja", "Procedimientos", 1890, "unidad", False, False),
    ]

    productos = []
    for codigo, nombre, desc, cat, precio, unidad, critico, receta in productos_data:
        productos.append(
            Producto(
                codigo=codigo, nombre=nombre, descripcion=desc, categoria=cat,
                precio=Decimal(precio), unidad=unidad, es_critico=critico,
                requiere_receta=receta,
            )
        )
    db.add_all(productos)
    db.commit()
    print(f"  {len(productos)} productos cargados")

    # Stock distribuido entre bodegas (random-ish pero deterministico)
    stocks = []
    for i, producto in enumerate(productos):
        cantidades = [50 + (i * 7) % 100, 30 + (i * 11) % 80, 20 + (i * 13) % 60,
                      15 + (i * 17) % 40, 10 + (i * 19) % 30]
        for bodega, cantidad in zip(bodegas, cantidades):
            stocks.append(
                StockBodega(
                    producto_id=producto.id, bodega_id=bodega.id,
                    cantidad=cantidad, lote=f"L-{producto.codigo[-3:]}-{bodega.codigo[-1]}",
                )
            )
    db.add_all(stocks)
    db.commit()
    print(f"  {len(stocks)} registros de stock cargados")


def main():
    crear_tablas()
    db = SessionLocal()
    try:
        if db.query(Producto).count() > 0:
            print("La BD ya contiene datos. Saltando seed.")
            return
        print("Cargando datos de prueba...")
        bodegas = cargar_bodegas(db)
        cargar_usuarios(db)
        cargar_productos_y_stock(db, bodegas)
        print("\nSeed completado.\n")
        print("Usuarios de prueba (password mostrado):")
        print("  admin@medistock.cl              / admin123")
        print("  ejecutivo@medistock.cl          / ejec123")
        print("  operador@medistock.cl           / oper123")
        print("  analista@medistock.cl           / anal123")
        print("  compras@clinicalasandes.cl      / clinica123")
        print("  paciente@gmail.com              / paciente123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
