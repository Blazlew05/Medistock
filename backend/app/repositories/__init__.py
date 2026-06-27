"""Capa de repositorios - acceso a base de datos."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.enums import EstadoOrden, RolUsuario
from backend.app.models import (
    Bodega,
    ItemOrden,
    Orden,
    Pago,
    Producto,
    StockBodega,
    Usuario,
)


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.db.get(Usuario, usuario_id)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Usuario]:
        return list(self.db.execute(select(Usuario).order_by(Usuario.id)).scalars())

    def list_by_rol(self, rol: RolUsuario) -> list[Usuario]:
        stmt = select(Usuario).where(Usuario.rol == rol)
        return list(self.db.execute(stmt).scalars())

    def create(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update(self, usuario: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(usuario)
        return usuario


class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, producto_id: int) -> Optional[Producto]:
        stmt = (
            select(Producto)
            .options(selectinload(Producto.stocks).selectinload(StockBodega.bodega))
            .where(Producto.id == producto_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_codigo(self, codigo: str) -> Optional[Producto]:
        stmt = (
            select(Producto)
            .options(selectinload(Producto.stocks).selectinload(StockBodega.bodega))
            .where(Producto.codigo == codigo)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self, solo_activos: bool = True, categoria: Optional[str] = None) -> list[Producto]:
        stmt = select(Producto).options(selectinload(Producto.stocks))
        if solo_activos:
            stmt = stmt.where(Producto.activo.is_(True))
        if categoria:
            stmt = stmt.where(Producto.categoria == categoria)
        stmt = stmt.order_by(Producto.nombre)
        return list(self.db.execute(stmt).scalars())

    def list_categorias(self) -> list[str]:
        stmt = select(Producto.categoria).distinct().order_by(Producto.categoria)
        return [row[0] for row in self.db.execute(stmt)]

    def create(self, producto: Producto) -> Producto:
        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def update(self, producto: Producto) -> Producto:
        self.db.commit()
        self.db.refresh(producto)
        return producto


class BodegaRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Bodega]:
        return list(self.db.execute(select(Bodega).order_by(Bodega.codigo)).scalars())

    def get_stock(self, producto_id: int, bodega_id: int) -> Optional[StockBodega]:
        stmt = select(StockBodega).where(
            StockBodega.producto_id == producto_id,
            StockBodega.bodega_id == bodega_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()


class OrdenRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, orden_id: int) -> Optional[Orden]:
        stmt = (
            select(Orden)
            .options(selectinload(Orden.items), selectinload(Orden.cliente))
            .where(Orden.id == orden_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_cliente(self, cliente_id: int) -> list[Orden]:
        stmt = (
            select(Orden)
            .where(Orden.cliente_id == cliente_id)
            .order_by(Orden.creada_en.desc())
        )
        return list(self.db.execute(stmt).scalars())

    def list_all(self, estado: Optional[EstadoOrden] = None) -> list[Orden]:
        stmt = select(Orden).options(selectinload(Orden.cliente))
        if estado:
            stmt = stmt.where(Orden.estado == estado)
        stmt = stmt.order_by(Orden.creada_en.desc())
        return list(self.db.execute(stmt).scalars())

    def list_para_operador(self) -> list[Orden]:
        """Ordenes priorizadas por urgencia para el operador logistico."""
        from sqlalchemy import case

        urgencia_orden = case(
            (Orden.urgencia == "alta", 1),
            (Orden.urgencia == "media", 2),
            (Orden.urgencia == "baja", 3),
            else_=4,
        )
        stmt = (
            select(Orden)
            .options(selectinload(Orden.items), selectinload(Orden.cliente))
            .where(Orden.estado.in_([
                EstadoOrden.PAGO_CONFIRMADO,
                EstadoOrden.EN_PREPARACION,
            ]))
            .order_by(urgencia_orden, Orden.creada_en)
        )
        return list(self.db.execute(stmt).scalars())

    def list_pendientes_aprobacion(self) -> list[Orden]:
        """Ordenes institucionales pendientes de aprobacion del ejecutivo."""
        stmt = (
            select(Orden)
            .options(selectinload(Orden.cliente), selectinload(Orden.items))
            .where(
                Orden.aprobada_por_ejecutivo.is_(False),
                Orden.estado == EstadoOrden.PENDIENTE_PAGO,
            )
            .order_by(Orden.creada_en.desc())
        )
        return list(self.db.execute(stmt).scalars())

    def create(self, orden: Orden) -> Orden:
        self.db.add(orden)
        self.db.commit()
        self.db.refresh(orden)
        return orden

    def update(self, orden: Orden) -> Orden:
        self.db.commit()
        self.db.refresh(orden)
        return orden


class PagoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pago_id: int) -> Optional[Pago]:
        return self.db.get(Pago, pago_id)

    def get_by_mercadopago_id(self, mp_id: str) -> Optional[Pago]:
        stmt = select(Pago).where(Pago.mercadopago_id == mp_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Pago]:
        return list(self.db.execute(select(Pago).order_by(Pago.creado_en.desc())).scalars())

    def create(self, pago: Pago) -> Pago:
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        return pago

    def update(self, pago: Pago) -> Pago:
        self.db.commit()
        self.db.refresh(pago)
        return pago
