"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Search, ShoppingCart, Package, AlertCircle } from "lucide-react";
import { api, formatCLP, type Producto } from "@/lib/api";
import { carrito } from "@/lib/carrito";

export default function CatalogoPage() {
  return (
    <Suspense fallback={<div className="text-center py-12 text-slate-500">Cargando catálogo...</div>}>
      <CatalogoContenido />
    </Suspense>
  );
}

function CatalogoContenido() {
  const params = useSearchParams();
  const categoriaInicial = params.get("categoria") || "";

  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [categoria, setCategoria] = useState(categoriaInicial);
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    api.get<string[]>("/api/v1/productos/categorias").then(setCategorias).catch(() => {});
  }, []);

  useEffect(() => {
    setCargando(true);
    const path = categoria
      ? `/api/v1/productos?categoria=${encodeURIComponent(categoria)}`
      : "/api/v1/productos";
    api.get<Producto[]>(path)
      .then(setProductos)
      .finally(() => setCargando(false));
  }, [categoria]);

  const productosFiltrados = productos.filter((p) =>
    busqueda
      ? p.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
        p.codigo.toLowerCase().includes(busqueda.toLowerCase())
      : true
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-ink">Catálogo</h1>
        <p className="text-slate-600 mt-1">{productos.length} productos disponibles</p>
      </div>

      <div className="grid md:grid-cols-[260px_1fr] gap-6">
        <aside className="space-y-4">
          <div className="card">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                className="input pl-9"
                placeholder="Buscar..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
            </div>
          </div>
          <div className="card">
            <h3 className="font-semibold text-ink mb-3">Categorías</h3>
            <div className="space-y-1">
              <button
                onClick={() => setCategoria("")}
                className={`w-full text-left rounded-md px-3 py-2 text-sm transition ${
                  !categoria ? "bg-primary-50 text-primary-700 font-semibold" : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                Todas
              </button>
              {categorias.map((c) => (
                <button
                  key={c}
                  onClick={() => setCategoria(c)}
                  className={`w-full text-left rounded-md px-3 py-2 text-sm transition ${
                    categoria === c ? "bg-primary-50 text-primary-700 font-semibold" : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <div>
          {cargando ? (
            <div className="text-center text-slate-500 py-12">Cargando productos...</div>
          ) : productosFiltrados.length === 0 ? (
            <div className="text-center text-slate-500 py-12">No se encontraron productos.</div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {productosFiltrados.map((p) => (
                <CardProducto key={p.codigo} producto={p} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CardProducto({ producto }: { producto: Producto }) {
  const [agregado, setAgregado] = useState(false);
  const sinStock = producto.stock_total <= 0;

  function agregar() {
    carrito.agregar(producto, 1);
    setAgregado(true);
    setTimeout(() => setAgregado(false), 1500);
  }

  return (
    <div className="card flex flex-col">
      <Link href={`/producto/${producto.codigo}`} className="flex-1">
        <div className="aspect-square rounded-lg bg-slate-100 flex items-center justify-center mb-3">
          <Package className="h-12 w-12 text-slate-400" />
        </div>
        <div className="text-xs text-slate-500 font-mono">{producto.codigo}</div>
        <h3 className="mt-1 font-semibold text-ink line-clamp-2">{producto.nombre}</h3>
        <div className="text-xs text-slate-600 mt-1">{producto.categoria}</div>
        {producto.requiere_receta && (
          <span className="mt-2 badge bg-amber-100 text-amber-800">
            <AlertCircle className="h-3 w-3 mr-1" /> Requiere receta
          </span>
        )}
      </Link>
      <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
        <div>
          <div className="text-lg font-bold text-ink">{formatCLP(producto.precio)}</div>
          <div className={`text-xs ${sinStock ? "text-red-600" : "text-emerald-600"}`}>
            {sinStock ? "Sin stock" : `Stock: ${producto.stock_total}`}
          </div>
        </div>
        <button
          onClick={agregar}
          disabled={sinStock}
          className="rounded-lg bg-primary-600 p-2 text-white hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Agregar al carrito"
        >
          {agregado ? "✓" : <ShoppingCart className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
}