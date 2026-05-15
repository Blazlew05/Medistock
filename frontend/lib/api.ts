import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  requireAuth = false
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (requireAuth) {
    const token = Cookies.get("medistock_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new ApiError(
      errorData.detail || `Error ${res.status}`,
      res.status
    );
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string, auth = false) => request<T>(path, { method: "GET" }, auth),
  post: <T>(path: string, body?: unknown, auth = false) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }, auth),
  put: <T>(path: string, body?: unknown, auth = true) =>
    request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }, auth),
  delete: <T>(path: string, auth = true) =>
    request<T>(path, { method: "DELETE" }, auth),
};

// ============== Auth helpers ==============
export function saveAuth(token: string, usuario: Usuario) {
  Cookies.set("medistock_token", token, { expires: 1 });
  Cookies.set("medistock_user", JSON.stringify(usuario), { expires: 1 });
}

export function getAuth(): { token: string | null; usuario: Usuario | null } {
  const token = Cookies.get("medistock_token") || null;
  const userStr = Cookies.get("medistock_user");
  return { token, usuario: userStr ? JSON.parse(userStr) : null };
}

export function clearAuth() {
  Cookies.remove("medistock_token");
  Cookies.remove("medistock_user");
}

// ============== Tipos ==============
export type RolUsuario =
  | "cliente_institucion"
  | "cliente_paciente"
  | "administrador"
  | "ejecutivo"
  | "operador_logistico"
  | "analista_finanzas";

export interface Usuario {
  id: number;
  email: string;
  nombre: string;
  rol: RolUsuario;
  empresa?: string;
  rut?: string;
  telefono?: string;
  direccion?: string;
  activo: boolean;
  creado_en: string;
}

export interface Producto {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: string;
  precio: number;
  unidad: string;
  stock_total: number;
  requiere_receta: boolean;
  imagen_url?: string;
}

export interface ProductoAdmin extends Producto {
  id: number;
  activo: boolean;
  es_critico: boolean;
}

export interface StockBodega {
  bodega_id: number;
  bodega_nombre: string;
  bodega_region: string;
  cantidad: number;
  lote?: string;
}

export interface ProductoConStock extends ProductoAdmin {
  stock_por_bodega: StockBodega[];
}

export interface ItemCarrito {
  producto: Producto;
  cantidad: number;
}

export interface ItemOrden {
  id: number;
  producto_id: number;
  nombre_producto: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

export type EstadoOrden =
  | "pendiente_pago"
  | "pago_confirmado"
  | "en_preparacion"
  | "despachado"
  | "entregado"
  | "cancelado";

export type Urgencia = "alta" | "media" | "baja";
export type TipoDespacho = "express" | "normal";

export interface Orden {
  id: number;
  numero: string;
  cliente_id: number;
  estado: EstadoOrden;
  urgencia: Urgencia;
  tipo_despacho: TipoDespacho;
  direccion_envio: string;
  subtotal: number;
  costo_envio: number;
  total: number;
  notas?: string;
  aprobada_por_ejecutivo: boolean;
  tracking_simulado?: string;
  creada_en: string;
  items: ItemOrden[];
}

export type EstadoPago = "pendiente" | "aprobado" | "rechazado" | "en_proceso";

export interface Pago {
  id: number;
  orden_id: number;
  mercadopago_id?: string;
  preference_id?: string;
  monto: number;
  estado: EstadoPago;
  metodo?: string;
  creado_en: string;
}

export const formatCLP = (n: number): string =>
  new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(n);
