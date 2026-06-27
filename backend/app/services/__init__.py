"""Capa de servicios - logica de negocio."""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.enums import EstadoOrden, EstadoPago, RolUsuario, TipoDespacho
from backend.app.core.security import hash_password, verify_password
from backend.app.integrations.mercadopago_client import mp_client
from backend.app.models import (
    ItemOrden,
    Orden,
    Pago,
    Producto,
    Usuario,
)
from backend.app.repositories import (
    BodegaRepository,
    OrdenRepository,
    PagoRepository,
    ProductoRepository,
    UsuarioRepository,
)
from backend.app.schemas import (
    OrdenCreate,
    ProductoCreate,
    ProductoUpdate,
    UsuarioCreate,
)

COSTO_ENVIO_EXPRESS = Decimal("5990")
COSTO_ENVIO_NORMAL = Decimal("2990")


# ============== AuthService ==============
class AuthService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def registrar(self, datos: UsuarioCreate) -> Usuario:
        if self.repo.get_by_email(datos.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya esta registrado",
            )
        usuario = Usuario(
            email=datos.email,
            password_hash=hash_password(datos.password),
            nombre=datos.nombre,
            rol=datos.rol,
            empresa=datos.empresa,
            rut=datos.rut,
            telefono=datos.telefono,
            direccion=datos.direccion,
        )
        return self.repo.create(usuario)

    def autenticar(self, email: str, password: str) -> Usuario:
        usuario = self.repo.get_by_email(email)
        if not usuario or not verify_password(password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales invalidas",
            )
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario desactivado",
            )
        return usuario


# ============== ProductoService ==============
class ProductoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductoRepository(db)
        self.bodega_repo = BodegaRepository(db)

    def listar(self, categoria: Optional[str] = None) -> list[Producto]:
        return self.repo.list_all(categoria=categoria)

    def listar_categorias(self) -> list[str]:
        return self.repo.list_categorias()

    def obtener_por_codigo(self, codigo: str) -> Producto:
        producto = self.repo.get_by_codigo(codigo)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {codigo} no encontrado",
            )
        return producto

    def obtener_por_id(self, producto_id: int) -> Producto:
        producto = self.repo.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto id={producto_id} no encontrado",
            )
        return producto

    def crear(self, datos: ProductoCreate) -> Producto:
        if self.repo.get_by_codigo(datos.codigo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un producto con codigo {datos.codigo}",
            )
        producto = Producto(**datos.model_dump())
        return self.repo.create(producto)

    def actualizar(self, producto_id: int, datos: ProductoUpdate) -> Producto:
        producto = self.obtener_por_id(producto_id)
        for k, v in datos.model_dump(exclude_unset=True).items():
            setattr(producto, k, v)
        return self.repo.update(producto)


# ============== OrdenService ==============
class OrdenService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrdenRepository(db)
        self.producto_repo = ProductoRepository(db)

    def _generar_numero(self) -> str:
        from datetime import datetime as dt

        return f"OC-{dt.now().strftime('%Y%m%d%H%M%S')}"

    def crear_orden(self, cliente: Usuario, datos: OrdenCreate) -> Orden:
        if not datos.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden debe contener al menos un item",
            )

        subtotal = Decimal("0")
        items_db: list[ItemOrden] = []

        for item_data in datos.items:
            producto = self.producto_repo.get_by_id(item_data.producto_id)
            if not producto or not producto.activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Producto id={item_data.producto_id} no disponible",
                )
            if producto.stock_total < item_data.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente para {producto.nombre}. "
                        f"Disponible: {producto.stock_total}, solicitado: {item_data.cantidad}"
                    ),
                )
            item_subtotal = producto.precio * item_data.cantidad
            subtotal += item_subtotal
            items_db.append(
                ItemOrden(
                    producto_id=producto.id,
                    nombre_producto=producto.nombre,
                    cantidad=item_data.cantidad,
                    precio_unitario=producto.precio,
                    subtotal=item_subtotal,
                )
            )

        costo_envio = (
            COSTO_ENVIO_EXPRESS
            if datos.tipo_despacho == TipoDespacho.EXPRESS
            else COSTO_ENVIO_NORMAL
        )
        total = subtotal + costo_envio

        # Las instituciones requieren aprobacion de ejecutivo antes de pagar
        requiere_aprobacion = cliente.rol == RolUsuario.CLIENTE_INSTITUCION

        orden = Orden(
            numero=self._generar_numero(),
            cliente_id=cliente.id,
            estado=EstadoOrden.PENDIENTE_PAGO,
            urgencia=datos.urgencia,
            tipo_despacho=datos.tipo_despacho,
            direccion_envio=datos.direccion_envio,
            subtotal=subtotal,
            costo_envio=costo_envio,
            total=total,
            notas=datos.notas,
            aprobada_por_ejecutivo=not requiere_aprobacion,
            items=items_db,
        )
        return self.repo.create(orden)

    def obtener(self, orden_id: int) -> Orden:
        orden = self.repo.get_by_id(orden_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden {orden_id} no encontrada",
            )
        return orden

    def listar_por_cliente(self, cliente_id: int) -> list[Orden]:
        return self.repo.list_by_cliente(cliente_id)

    def listar_todas(self, estado: Optional[EstadoOrden] = None) -> list[Orden]:
        return self.repo.list_all(estado=estado)

    def listar_para_operador(self) -> list[Orden]:
        return self.repo.list_para_operador()

    def listar_pendientes_aprobacion(self) -> list[Orden]:
        return self.repo.list_pendientes_aprobacion()

    def aprobar_por_ejecutivo(self, orden_id: int) -> Orden:
        orden = self.obtener(orden_id)
        orden.aprobada_por_ejecutivo = True
        return self.repo.update(orden)

    def cambiar_estado(self, orden_id: int, nuevo_estado: EstadoOrden) -> Orden:
        orden = self.obtener(orden_id)
        orden.estado = nuevo_estado
        # Si se despacha, generamos un tracking mock placeholder
        if nuevo_estado == EstadoOrden.DESPACHADO and not orden.tracking_simulado:
            orden.tracking_simulado = f"MED-{orden.numero[-8:]}"
        return self.repo.update(orden)


# ============== PagoService ==============
class PagoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PagoRepository(db)
        self.orden_repo = OrdenRepository(db)

    def iniciar_pago(self, orden_id: int, cliente: Usuario) -> dict:
        orden = self.orden_repo.get_by_id(orden_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada"
            )
        if orden.cliente_id != cliente.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La orden no pertenece al cliente",
            )
        if not orden.aprobada_por_ejecutivo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La orden aun no fue aprobada por un ejecutivo",
            )
        if orden.estado != EstadoOrden.PENDIENTE_PAGO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La orden no esta pendiente de pago (estado actual: {orden.estado})",
            )

        descripcion = f"MEDISTOCK - Orden {orden.numero}"
        respuesta_mp = mp_client.crear_preferencia(
            orden_numero=orden.numero,
            descripcion=descripcion,
            monto=float(orden.total),
            comprador_email=cliente.email,
        )

        pago = Pago(
            orden_id=orden.id,
            preference_id=respuesta_mp["id"],
            monto=orden.total,
            estado=EstadoPago.PENDIENTE,
        )
        self.repo.create(pago)

        return {
            "pago_id": pago.id,
            "preference_id": respuesta_mp["id"],
            "init_point": respuesta_mp.get("init_point", ""),
            "sandbox_init_point": respuesta_mp.get("sandbox_init_point", ""),
        }

    def procesar_webhook(self, payment_id: str) -> Optional[Pago]:
        info = mp_client.consultar_pago(payment_id)
        external_ref = info.get("external_reference")
        if not external_ref:
            return None

        from sqlalchemy import select
        stmt = select(Orden).where(Orden.numero == external_ref)
        orden = self.db.execute(stmt).scalar_one_or_none()
        if not orden:
            return None

        pago = next((p for p in orden.pagos if p.preference_id), None)
        if not pago:
            return None

        pago.mercadopago_id = str(info.get("id"))
        pago.metodo = info.get("payment_method_id")
        mp_status = info.get("status")
        if mp_status == "approved":
            pago.estado = EstadoPago.APROBADO
            orden.estado = EstadoOrden.PAGO_CONFIRMADO
        elif mp_status == "rejected":
            pago.estado = EstadoPago.RECHAZADO
        else:
            pago.estado = EstadoPago.EN_PROCESO

        self.db.commit()
        return pago

    def listar_para_auditoria(self) -> list[Pago]:
        return self.repo.list_all()

    def auditar(self, pago_id: int, analista: Usuario, nuevo_estado: EstadoPago) -> Pago:
        pago = self.repo.get_by_id(pago_id)
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado"
            )
        pago.estado = nuevo_estado
        pago.auditado_por = analista.id
        pago.auditado_en = datetime.now(timezone.utc)
        return self.repo.update(pago)
