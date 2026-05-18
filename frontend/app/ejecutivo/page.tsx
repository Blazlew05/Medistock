"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Building2, Search, Warehouse } from "lucide-react";
import { AuthGuard } from "@/componentes/AuthGuard";
import { api, formatCLP, type Orden, type ProductoConStock } from "@/lib/api";

export default function EjecutivoPage() {
  return (
    <AuthGuard rolesPermitidos={["ejecutivo", "administrador"]}>
      {() => <EjecutivoLayout />}
    </AuthGuard>
  );
}

function EjecutivoLayout() {
  const [tab, setTab] = useState<"aprobar" | "stock">("aprobar");

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-ink">Ejecutivo de cuentas</h1>
        <p className="text-slate-600">Aprobación de órdenes institucionales y consulta de stock</p>
      </div>

      <div className="flex gap-2 border-b border-slate-200 mb-6">
        <button onClick={() => setTab("aprobar")} className={`px-4 py-3 text-sm font-semibold border-b-2 ${tab === "aprobar" ? "border-primary-600 text-primary-700" : "border-transparent text-slate-600"}`}>
          Pendientes de aprobación
        </button>
        <button onClick={() => setTab("stock")} className={`px-4 py-3 text-sm font-semibold border-b-2 ${tab === "stock" ? "border-primary-600 text-primary-700" : "border-transparent text-slate-600"}`}>
          Stock multi-bodega
        </button>
      </div>

      {tab === "aprobar" ? <PendientesAprobacion /> : <StockMultiBodega />}
    </div>
  );
}

function PendientesAprobacion() {
  const [ordenes, setOrdenes] = useState<Orden[]>([]);
  const [cargando, setCargando] = useState(true);

  function cargar() {
    setCargando(true);
    api.get<Orden[]>("/api/v1/ejecutivo/ordenes/pendientes", true)
      .then(setOrdenes)
      .finally(() => setCargando(false));
  }
  useEffect(() => { cargar(); }, []);

  async function aprobar(id: number) {
    if (!confirm("¿Aprobar esta orden? El cliente podrá proceder al pago.")) return;
    await api.post(`/api/v1/ejecutivo/ordenes/${id}/aprobar`, null, true);
    cargar();
  }

  if (cargando) return <div className="text-center py-12 text-slate-500">Cargando...</div>;

  if (ordenes.length === 0) {
    return (
      <div className="card text-center py-12">
        <CheckCircle2 className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
        <p className="text-slate-600">No hay órdenes pendientes de aprobación.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {ordenes.map((o) => (
        <div key={o.id} className="card">
          <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
            <div>
              <div className="flex items-center gap-2">
                <Building2 className="h-4 w-4 text-primary-600" />
                <span className="text-xs text-slate-500 font-mono">{o.numero}</span>
              </div>
              <div className="text-sm text-slate-600 mt-1">{new Date(o.creada_en).toLocaleString("es-CL")}</div>
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-ink">{formatCLP(o.total)}</div>
              <span className={`badge ${o.urgencia === "alta" ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800"}`}>
                Urgencia: {o.urgencia}
              </span>
            </div>
          </div>

          <div className="bg-slate-50 rounded-lg p-3 text-sm">
            <div className="font-semibold mb-2">Items:</div>
            <ul className="space-y-1 text-slate-700">
              {o.items.map((it) => (
                <li key={it.id} className="flex justify-between">
                  <span>{it.nombre_producto} × {it.cantidad}</span>
                  <span className="text-slate-600">{formatCLP(it.subtotal)}</span>
                </li>
              ))}
            </ul>
            <div className="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-600">
              Despacho: {o.tipo_despacho} · {o.direccion_envio}
            </div>
            {o.notas && <div className="mt-1 text-xs text-slate-600">Notas: {o.notas}</div>}
          </div>

          <div className="mt-3 flex justify-end">
            <button onClick={() => aprobar(o.id)} className="btn-primary">
              <CheckCircle2 className="h-4 w-4" /> Aprobar orden
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function StockMultiBodega() {
  const [productoId, setProductoId] = useState("");
  const [datos, setDatos] = useState<ProductoConStock | null>(null);
  const [error, setError] = useState("");

  async function buscar(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const res = await api.get<ProductoConStock>(`/api/v1/ejecutivo/productos/${productoId}/stock`, true);
      setDatos(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No encontrado");
      setDatos(null);
    }
  }

  return (
    <div>
      <form onSubmit={buscar} className="card mb-4 flex gap-2">
        <input className="input flex-1" placeholder="ID del producto (ej: 1, 2, 3...)" value={productoId} onChange={(e) => setProductoId(e.target.value)} />
        <button type="submit" className="btn-primary">
          <Search className="h-4 w-4" /> Buscar
        </button>
      </form>

      {error && <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">{error}</div>}

      {datos && (
        <div className="card">
          <div className="border-b border-slate-200 pb-3 mb-3">
            <div className="text-xs font-mono text-slate-500">{datos.codigo}</div>
            <h3 className="text-xl font-bold text-ink mt-1">{datos.nombre}</h3>
            <div className="flex gap-3 mt-2 text-sm">
              <span className="text-slate-600">{datos.categoria}</span>
              <span className="font-semibold text-ink">{formatCLP(datos.precio)}</span>
              <span className="text-emerald-700">Total: {datos.stock_total}</span>
            </div>
          </div>

          <h4 className="font-semibold text-ink mb-3 flex items-center gap-2">
            <Warehouse className="h-4 w-4 text-primary-600" /> Distribución por bodega
          </h4>
          <div className="space-y-2">
            {datos.stock_por_bodega.map((s) => (
              <div key={s.bodega_id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                <div>
                  <div className="font-medium text-ink">{s.bodega_nombre}</div>
                  <div className="text-xs text-slate-500">{s.bodega_region} · Lote: {s.lote || "—"}</div>
                </div>
                <div className="font-bold text-primary-700">{s.cantidad}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
