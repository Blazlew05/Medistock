import { Package, ShieldCheck, Truck, Clock, ArrowRight, Activity } from "lucide-react";
import Link from "next/link";

interface Producto {
  id: number;
  codigo: string;
  nombre: string;
  categoria: string;
  precio: number;
  stock_total: number;
  requiere_receta: boolean;
}

const API = process.env.NEXT_PUBLIC_MEDISTOCK_API || "http://localhost:8000";

async function obtenerDestacados(): Promise<Producto[]> {
  try {
    const res = await fetch(`${API}/api/v1/productos`, { cache: "no-store" });
    if (!res.ok) return [];
    const data: Producto[] = await res.json();
    // tomamos productos sin receta, con stock, y un mix de categorias
    return data
      .filter((p) => !p.requiere_receta && p.stock_total > 0)
      .slice(0, 8);
  } catch {
    return [];
  }
}

const CLP = (n: number) =>
  new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(n);

export default async function Home() {
  const productos = await obtenerDestacados();

  return (
    <div>
      {/* HERO */}
      <section className="bg-gradient-to-br from-amarilla-400 to-amarilla-600 py-16">
        <div className="mx-auto max-w-7xl px-4 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-amarilla-900 tracking-tight">
              Salud al alcance<br />de toda tu familia
            </h1>
            <p className="mt-4 text-lg text-amarilla-900/80">
              Productos farmacéuticos y de cuidado personal con la confianza
              de más de 40 años en el mercado.
            </p>
            <Link href="/catalogo" className="mt-6 inline-flex items-center gap-2 bg-amarilla-900 text-white px-6 py-3 rounded-lg font-semibold hover:bg-amarilla-800">
              Ver catálogo completo <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="hidden md:grid grid-cols-2 gap-3">
            {[
              { i: ShieldCheck, t: "Productos certificados" },
              { i: Truck, t: "Despacho a domicilio" },
              { i: Clock, t: "Atención 24/7" },
              { i: Package, t: "47 sucursales" },
            ].map((c, i) => (
              <div key={i} className="bg-white/90 rounded-xl p-4">
                <c.i className="h-6 w-6 text-amarilla-700" />
                <div className="text-sm font-semibold text-amarilla-900 mt-2">{c.t}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integracion API */}
      <section className="bg-amarilla-50 border-b border-amarilla-200 py-3">
        <div className="mx-auto max-w-7xl px-4 flex items-center justify-center gap-2 text-xs text-amarilla-900">
          <Activity className="h-3 w-3" />
          <span>
            <strong>Catálogo en vivo:</strong> conectado con la API de <strong>MEDISTOCK</strong> ·
            stock actualizado en tiempo real
          </span>
        </div>
      </section>

      {/* Productos destacados */}
      <section className="mx-auto max-w-7xl px-4 py-12">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-2xl font-bold text-amarilla-900">Más vendidos</h2>
            <p className="text-sm text-amarilla-800/70">Lo que la gente está comprando hoy</p>
          </div>
          <Link href="/catalogo" className="text-sm font-semibold text-amarilla-700 hover:underline">
            Ver todos →
          </Link>
        </div>

        {productos.length === 0 ? (
          <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-900">
            <strong>⚠️ Sin conexión con MEDISTOCK API.</strong> Verifica que el backend esté
            corriendo en <code>{API}</code>.
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {productos.map((p) => (
              <div key={p.codigo} className="bg-white rounded-xl border border-amarilla-200 p-4 hover:shadow-md transition">
                <div className="aspect-square bg-amarilla-50 rounded-lg flex items-center justify-center mb-3">
                  <Package className="h-10 w-10 text-amarilla-400" />
                </div>
                <div className="text-xs text-amarilla-600 uppercase tracking-wide font-semibold">{p.categoria}</div>
                <div className="font-bold text-amarilla-900 mt-1 line-clamp-2 text-sm leading-tight">{p.nombre}</div>
                <div className="text-lg font-extrabold text-amarilla-800 mt-2">{CLP(p.precio)}</div>
                <button className="w-full mt-3 bg-amarilla-500 hover:bg-amarilla-600 text-amarilla-900 font-bold py-2 rounded-lg text-sm">
                  Agregar
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Categorías */}
      <section className="bg-white border-t border-amarilla-200 py-12">
        <div className="mx-auto max-w-7xl px-4">
          <h2 className="text-2xl font-bold text-amarilla-900 mb-6">Compra por categoría</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {["Material Descartable", "Equipamiento", "Soluciones", "Farmacos", "Procedimientos"].map((c) => (
              <Link
                key={c}
                href={`/catalogo?categoria=${encodeURIComponent(c)}`}
                className="bg-amarilla-50 hover:bg-amarilla-100 border border-amarilla-200 rounded-xl p-4 text-center transition"
              >
                <Package className="h-8 w-8 text-amarilla-700 mx-auto mb-2" />
                <div className="font-semibold text-amarilla-900 text-sm">{c}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
