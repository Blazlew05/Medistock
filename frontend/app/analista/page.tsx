"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, XCircle, Clock, DollarSign } from "lucide-react";
import { AuthGuard } from "@/componentes/AuthGuard";
import { api, formatCLP, type Pago, type EstadoPago } from "@/lib/api";

const ETIQUETAS: Record<EstadoPago, { label: string; color: string; icon: any }> = {
  pendiente: { label: "Pendiente", color: "bg-slate-100 text-slate-800", icon: Clock },
  en_proceso: { label: "En proceso", color: "bg-amber-100 text-amber-800", icon: Clock },
  aprobado: { label: "Aprobado", color: "bg-emerald-100 text-emerald-800", icon: CheckCircle2 },
  rechazado: { label: "Rechazado", color: "bg-red-100 text-red-800", icon: XCircle },
};

export default function AnalistaPage() {
  return (
    <AuthGuard rolesPermitidos={["analista_finanzas", "administrador"]}>
      {() => <AnalistaVista />}
    </AuthGuard>
  );
}

function AnalistaVista() {
  const [pagos, setPagos] = useState<Pago[]>([]);
  const [cargando, setCargando] = useState(true);

  function cargar() {
    setCargando(true);
    api.get<Pago[]>("/api/v1/analista/pagos", true)
      .then(setPagos)
      .finally(() => setCargando(false));
  }
  useEffect(() => { cargar(); }, []);

  async function auditar(pagoId: number, estado: EstadoPago) {
    if (!confirm(`¿Marcar pago #${pagoId} como ${estado}?`)) return;
    await api.post(`/api/v1/analista/pagos/${pagoId}/auditar`, { estado }, true);
    cargar();
  }

  const totalAprobado = pagos
    .filter((p) => p.estado === "aprobado")
    .reduce((acc, p) => acc + p.monto, 0);
  const totalPendiente = pagos
    .filter((p) => p.estado === "pendiente" || p.estado === "en_proceso")
    .reduce((acc, p) => acc + p.monto, 0);

  if (cargando) return <div className="text-center py-12 text-slate-500">Cargando...</div>;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-ink">Analista de finanzas</h1>
        <p className="text-slate-600">Auditoría y conciliación de pagos</p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4 mb-6">
        <div className="card">
          <div className="text-sm text-slate-600">Total pagos</div>
          <div className="text-2xl font-bold text-ink mt-1">{pagos.length}</div>
        </div>
        <div className="card bg-emerald-50 border-emerald-200">
          <div className="flex items-center gap-2 text-emerald-800">
            <DollarSign className="h-4 w-4" /> Aprobado
          </div>
          <div className="text-2xl font-bold text-emerald-900 mt-1">{formatCLP(totalAprobado)}</div>
        </div>
        <div className="card bg-amber-50 border-amber-200">
          <div className="flex items-center gap-2 text-amber-800">
            <Clock className="h-4 w-4" /> Pendiente
          </div>
          <div className="text-2xl font-bold text-amber-900 mt-1">{formatCLP(totalPendiente)}</div>
        </div>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-600 border-b border-slate-200">
            <tr>
              <th className="pb-3 font-semibold">ID</th>
              <th className="pb-3 font-semibold">Orden</th>
              <th className="pb-3 font-semibold">MP ID</th>
              <th className="pb-3 font-semibold">Método</th>
              <th className="pb-3 font-semibold">Fecha</th>
              <th className="pb-3 font-semibold text-right">Monto</th>
              <th className="pb-3 font-semibold">Estado</th>
              <th className="pb-3 font-semibold text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {pagos.map((p) => {
              const E = ETIQUETAS[p.estado];
              return (
                <tr key={p.id} className="border-b border-slate-100">
                  <td className="py-3 font-mono">#{p.id}</td>
                  <td className="py-3">#{p.orden_id}</td>
                  <td className="py-3 font-mono text-xs">{p.mercadopago_id || "—"}</td>
                  <td className="py-3">{p.metodo || "—"}</td>
                  <td className="py-3 text-slate-600">{new Date(p.creado_en).toLocaleDateString("es-CL")}</td>
                  <td className="py-3 text-right font-semibold">{formatCLP(p.monto)}</td>
                  <td className="py-3">
                    <span className={`badge ${E.color} flex w-fit items-center gap-1`}>
                      <E.icon className="h-3 w-3" /> {E.label}
                    </span>
                  </td>
                  <td className="py-3 text-right">
                    {p.estado !== "aprobado" && (
                      <button onClick={() => auditar(p.id, "aprobado")} className="text-emerald-600 hover:text-emerald-800 p-1" title="Aprobar">
                        <CheckCircle2 className="h-4 w-4" />
                      </button>
                    )}
                    {p.estado !== "rechazado" && (
                      <button onClick={() => auditar(p.id, "rechazado")} className="text-red-600 hover:text-red-800 p-1" title="Rechazar">
                        <XCircle className="h-4 w-4" />
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {pagos.length === 0 && <div className="text-center py-8 text-slate-500">Aún no hay pagos registrados.</div>}
      </div>
    </div>
  );
}
