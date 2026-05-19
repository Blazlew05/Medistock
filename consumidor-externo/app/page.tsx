"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Package, AlertCircle, Search } from "lucide-react";

interface Producto {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  categoria: string;
  precio: number;
  unidad: string;
  stock_total: number;
  requiere_receta: boolean;
}

const API = process.env.NEXT_PUBLIC_MEDISTOCK_API || "http://localhost:8000";
const CLP = (n: number) =>
  new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(n);

export default function CatalogoPage() {
  return (
    <Suspense fallback={<div className="text-center py-12 text-amarilla-700">Cargando catálogo...</div>}>
      <CatalogoContenido />
    </Suspense>
  );
}

function CatalogoContenido() {
  const params = useSearchParams();
  const catInicial = params.get("categoria") || "";

  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [categoria, setCategoria] = useState(catInicial);
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [errorApi, setErrorApi] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/v1/productos/categorias`)
      .then((r) => r.json())
      .then(setCategorias)
      .catch(() => setErrorApi(true));
  }, []);

  useEffect(() => {
    setCargando(true);
    const url = categoria
      ? `${API}/api/v1/productos?categoria=${encodeURIComponent(categoria)}`
      : `${API}/api/v1/productos`;
    fetch(url)
      .then((r) => r.json())
      .then((data) => { setProductos(data); setErrorApi(false); })
      .catch(() => setErrorApi(true))
      .finally(() => setCargando(false));
  }, [categoria]);

  const filtrados = productos.filter((p) =>
    busqueda
      ? p.nombre.toLowerCase().includes(busqueda.toLowerCase())
      : true
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-extrabold text-amarilla-900">Catálogo</h1>
        <p className="text-amarilla-800/70">{productos.length} productos · datos en vivo desde MEDISTOCK</p>
      </div>

      {errorApi && (
        <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-900">
          <strong>Error de conexión:</strong> no se pudo conectar con MEDISTOCK API ({API}).
        </div>
      )}

      <div className="grid md:grid-cols-[240px_1fr] gap-6">
        <aside className="space-y-3">
          <div className="bg-white rounded-xl border border-amarilla-200 p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-amarilla-500" />
              <input
                className="w-full pl-9 pr-3 py-2 border border-amarilla-300 rounded-lg text-sm"
                placeholder="Buscar..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
            </div>
          </div>
          <div className="bg-white rounded-xl border border-amarilla-200 p-4">
            <h3 className="font-bold text-amarilla-900 mb-2">Categorías</h3>
            <div className="space-y-1">
              <button onClick={() => setCategoria("")} className={`w-full text-left px-3 py-2 rounded text-sm ${!categoria ? "bg-amarilla-100 text-amarilla-900 font-bold" : "text-amarilla-800"}`}>
                Todas
              </button>
              {categorias.map((c) => (
                <button key={c} onClick={() => setCategoria(c)} className={`w-full text-left px-3 py-2 rounded text-sm ${categoria === c ? "bg-amarilla-100 text-amarilla-900 font-bold" : "text-amarilla-800 hover:bg-amarilla-50"}`}>
                  {c}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <div>
          {cargando ? (
            <div className="text-center py-12 text-amarilla-700">Cargando productos...</div>
          ) : filtrados.length === 0 ? (
            <div className="text-center py-12 text-amarilla-700">No hay productos.</div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtrados.map((p) => (
                <div key={p.codigo} className="bg-white rounded-xl border border-amarilla-200 p-4">
                  <div className="aspect-square bg-amarilla-50 rounded-lg flex items-center justify-center mb-3">
                    <Package className="h-12 w-12 text-amarilla-400" />
                  </div>
                  <div className="text-xs font-mono text-amarilla-600">{p.codigo}</div>
                  <h3 className="font-bold text-amarilla-900 mt-1 line-clamp-2 text-sm">{p.nombre}</h3>
                  <div className="text-xs text-amarilla-700 mt-1">{p.categoria}</div>
                  {p.requiere_receta && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-red-700">
                      <AlertCircle className="h-3 w-3" /> Requiere receta
                    </div>
                  )}
                  <div className="mt-3 flex items-end justify-between">
                    <div>
                      <div className="text-xl font-extrabold text-amarilla-900">{CLP(p.precio)}</div>
                      <div className="text-xs text-amarilla-700">Stock: {p.stock_total}</div>
                    </div>
                    <button className="bg-amarilla-500 hover:bg-amarilla-600 text-amarilla-900 font-bold px-3 py-1.5 rounded text-xs">
                      Comprar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}