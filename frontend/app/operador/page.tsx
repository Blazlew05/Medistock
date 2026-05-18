"use client";

import { useEffect, useState } from "react";
import { Package, Truck, CheckCircle2, AlertTriangle } from "lucide-react";
import { AuthGuard } from "@/componentes/AuthGuard";
import { api, formatCLP, type Orden } from "@/lib/api";

export default function OperadorPage() {
  return (
    <AuthGuard rolesPermitidos={["operador_logistico", "administrador"]}>
      {() => <OperadorVista />}
    </AuthGuard>
  );
}

function OperadorVista() {
  const [ordenes, setOrdenes] = useState<Orden[]>([]);
  const [cargando, setCargando] = useState(true);

  function cargar() {
    setCargando(true);
    api.get<Orden[]>("/api/v1/operador/ordenes/priorizadas", true)
      .then(setOrdenes)
      .finally(() => setCargando(false));
  }
  useEffect(() => { cargar(); }, []);

  async function cambiar(id: number, accion: "preparar" | "despachar" | "entregar") {
    await api.post(`/api/v1/operador/ordenes/${id}/${accion}`, null, true);
    cargar();
  }

  const altas = ordenes.filter((o) => o.urgencia === "alta");
  const medias = ordenes.filter((o) => o.urgencia === "media");
  const bajas = ordenes.filter((o) => o.urgencia === "baja");

  if (cargando) return <div className="text-center py-12 text-slate-500">Cargando...</div>;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-ink">Operador logístico</h1>
        <p className="text-slate-600">Órdenes pagadas priorizadas por urgencia médica</p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4 mb-6">
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center gap-2 text-red-800">
            <AlertTriangle className="h-5 w-5" />
            <span className="font-semibold">Urgencia ALTA</span>
          </div>
          <div className="text-3xl font-bold text-red-900 mt-2">{altas.length}</div>
        </div>
        <div className="card bg-amber-50 border-amber-200">
          <div className="flex items-center gap-2 text-amber-800">
            <Package className="h-5 w-5" />
            <span className="font-semibold">Urgencia media</span>
          </div>
          <div className="text-3xl font-bold text-amber-900 mt-2">{medias.length}</div>
        </div>
        <div className="card bg-slate-50">
          <div className="flex items-center gap-2 text-slate-700">
            <Package className="h-5 w-5" />
            <span className="font-semibold">Urgencia baja</span>
          </div>
          <div className="text-3xl font-bold text-slate-900 mt-2">{bajas.length}</div>
        </div>
      </div>

      {ordenes.length === 0 ? (
        <div className="card text-center py-12">
          <CheckCircle2 className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
          <p className="text-slate-600">No hay órdenes pendientes de preparación.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {ordenes.map((o) => (
            <div key={o.id} className={`card ${o.urgencia === "alta" ? "border-l-4 border-l-red-500" : ""}`}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-mono text-slate-500">{o.numero}</span>
                    <span className={`badge ${o.urgencia === "alta" ? "bg-red-100 text-red-800" : o.urgencia === "media" ? "bg-amber-100 text-amber-800" : "bg-slate-100"}`}>
                      Urgencia {o.urgencia}
                    </span>
                    <span className="badge bg-blue-100 text-blue-800">
                      {o.estado.replace(/_/g, " ")}
                    </span>
                    {o.tipo_despacho === "express" && (
                      <span className="badge bg-primary-100 text-primary-800">EXPRESS 24h</span>
                    )}
                  </div>
                  <div className="text-sm text-slate-700 mb-2">
                    <strong>Dirección:</strong> {o.direccion_envio}
                  </div>
                  <details className="text-sm">
                    <summary className="cursor-pointer text-primary-700 font-medium">Ver items ({o.items.length})</summary>
                    <ul className="mt-2 space-y-1 text-slate-700 bg-slate-50 rounded p-3">
                      {o.items.map((it) => (
                        <li key={it.id}>• {it.nombre_producto} × <strong>{it.cantidad}</strong></li>
                      ))}
                    </ul>
                  </details>
                  {o.tracking_simulado && (
                    <div className="mt-2 text-xs font-mono text-primary-700">Tracking: {o.tracking_simulado}</div>
                  )}
                </div>
                <div className="flex flex-col gap-2 min-w-[180px]">
                  {o.estado === "pago_confirmado" && (
                    <button onClick={() => cambiar(o.id, "preparar")} className="btn-primary text-sm">
                      <Package className="h-4 w-4" /> Iniciar preparación
                    </button>
                  )}
                  {o.estado === "en_preparacion" && (
                    <button onClick={() => cambiar(o.id, "despachar")} className="btn-primary text-sm">
                      <Truck className="h-4 w-4" /> Despachar
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
