"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Package, Clock, Truck, CheckCircle2, XCircle } from "lucide-react";
import { AuthGuard } from "@/components/AuthGuard";
import { api, formatCLP, type Orden, type EstadoOrden } from "@/lib/api";

const ETIQUETAS: Record<EstadoOrden, { label: string; color: string; icon: any }> = {
  pendiente_pago: { label: "Pendiente de pago", color: "bg-amber-100 text-amber-800", icon: Clock },
  pago_confirmado: { label: "Pago confirmado", color: "bg-blue-100 text-blue-800", icon: CheckCircle2 },
  en_preparacion: { label: "En preparación", color: "bg-indigo-100 text-indigo-800", icon: Package },
  despachado: { label: "Despachado", color: "bg-primary-100 text-primary-800", icon: Truck },
  entregado: { label: "Entregado", color: "bg-emerald-100 text-emerald-800", icon: CheckCircle2 },
  cancelado: { label: "Cancelado", color: "bg-red-100 text-red-800", icon: XCircle },
};

export default function MisPedidosPage() {
  return (
    <AuthGuard rolesPermitidos={["cliente_paciente", "cliente_institucion"]}>
      {() => <MisPedidos />}
    </AuthGuard>
  );
}

function MisPedidos() {
  const [ordenes, setOrdenes] = useState<Orden[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    api.get<Orden[]>("/api/v1/ordenes/mis", true)
      .then(setOrdenes)
      .finally(() => setCargando(false));
  }, []);

  if (cargando) return <div className="text-center py-12 text-slate-500">Cargando...</div>;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold text-ink mb-6">Mis pedidos</h1>

      {ordenes.length === 0 ? (
        <div className="card text-center py-12">
          <Package className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-600">Aún no tienes pedidos.</p>
          <Link href="/catalogo" className="btn-primary mt-4">Ver catálogo</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {ordenes.map((o) => {
            const E = ETIQUETAS[o.estado];
            return (
              <div key={o.id} className="card">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="text-xs text-slate-500 font-mono">{o.numero}</div>
                    <div className="text-sm text-slate-600">{new Date(o.creada_en).toLocaleString("es-CL")}</div>
                  </div>
                  <div className={`badge ${E.color} flex items-center gap-1`}>
                    <E.icon className="h-3 w-3" /> {E.label}
                  </div>
                </div>
                <div className="mt-3 flex items-end justify-between">
                  <div>
                    <div className="text-sm text-slate-600">{o.tipo_despacho === "express" ? "Despacho express" : "Despacho normal"}</div>
                    {o.tracking_simulado && (
                      <div className="text-xs text-primary-700 font-mono mt-1">Tracking: {o.tracking_simulado}</div>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-ink">{formatCLP(o.total)}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
