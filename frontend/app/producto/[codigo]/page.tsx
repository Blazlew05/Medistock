"use client";

import { useEffect, useState, use } from "react";
import { Package, AlertCircle, ShoppingCart, Truck, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { api, formatCLP, type Producto } from "@/lib/api";
import { carrito } from "@/lib/carrito";

export default function ProductoDetallePage({ params }: { params: Promise<{ codigo: string }> }) {
  const { codigo } = use(params);
  const [producto, setProducto] = useState<Producto | null>(null);
  const [cantidad, setCantidad] = useState(1);
  const [agregado, setAgregado] = useState(false);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    api.get<Producto>(`/api/v1/productos/${codigo}`)
      .then(setProducto)
      .finally(() => setCargando(false));
  }, [codigo]);

  if (cargando) return <div className="text-center py-12 text-slate-500">Cargando...</div>;
  if (!producto) return <div className="text-center py-12 text-slate-500">Producto no encontrado</div>;

  function agregarAlCarrito() {
    carrito.agregar(producto!, cantidad);
    setAgregado(true);
    setTimeout(() => setAgregado(false), 2000);
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link href="/catalogo" className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-primary-700 mb-6">
        <ArrowLeft className="h-4 w-4" /> Volver al catálogo
      </Link>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="aspect-square rounded-2xl bg-slate-100 flex items-center justify-center">
          <Package className="h-32 w-32 text-slate-300" />
        </div>

        <div>
          <div className="text-xs text-slate-500 font-mono">{producto.codigo}</div>
          <h1 className="text-3xl font-bold text-ink mt-1">{producto.nombre}</h1>
          <div className="text-sm text-slate-600 mt-1">{producto.categoria}</div>

          {producto.requiere_receta && (
            <div className="mt-4 flex items-start gap-2 rounded-lg bg-amber-50 border border-amber-200 p-3 text-sm text-amber-800">
              <AlertCircle className="h-4 w-4 mt-0.5" />
              <div>Este producto requiere receta médica. Deberás presentarla al momento de la entrega.</div>
            </div>
          )}

          <p className="mt-6 text-slate-700">{producto.descripcion}</p>

          <div className="mt-6 flex items-baseline gap-3">
            <div className="text-4xl font-bold text-ink">{formatCLP(producto.precio)}</div>
            <div className="text-sm text-slate-500">/ {producto.unidad}</div>
          </div>

          <div className={`mt-2 text-sm font-medium ${producto.stock_total > 0 ? "text-emerald-700" : "text-red-700"}`}>
            {producto.stock_total > 0 ? `${producto.stock_total} en stock` : "Sin stock"}
          </div>

          <div className="mt-6 flex items-end gap-3">
            <div>
              <label className="label">Cantidad</label>
              <div className="flex items-center">
                <button onClick={() => setCantidad(Math.max(1, cantidad - 1))} className="rounded-l-lg border border-slate-300 bg-white px-3 py-2 hover:bg-slate-50">-</button>
                <input type="number" min={1} max={producto.stock_total} value={cantidad} onChange={(e) => setCantidad(Math.max(1, parseInt(e.target.value) || 1))} className="w-20 border-y border-slate-300 px-3 py-2 text-center" />
                <button onClick={() => setCantidad(Math.min(producto.stock_total, cantidad + 1))} className="rounded-r-lg border border-slate-300 bg-white px-3 py-2 hover:bg-slate-50">+</button>
              </div>
            </div>
            <button onClick={agregarAlCarrito} disabled={producto.stock_total <= 0} className="btn-primary flex-1 py-3">
              <ShoppingCart className="h-4 w-4" />
              {agregado ? "Agregado ✓" : "Agregar al carrito"}
            </button>
          </div>

          <div className="mt-6 rounded-lg bg-slate-50 border border-slate-200 p-4 text-sm text-slate-700">
            <div className="flex items-center gap-2 font-semibold mb-2">
              <Truck className="h-4 w-4 text-primary-600" /> Opciones de despacho
            </div>
            <ul className="space-y-1 text-slate-600">
              <li>• Express (24h en Región Metropolitana) — $5.990</li>
              <li>• Normal (72h en todo Chile continental) — $2.990</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
