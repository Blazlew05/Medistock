"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ShoppingCart, User, LogOut, Activity, Menu, X } from "lucide-react";
import { carrito } from "@/lib/carrito";
import { clearAuth, getAuth, type Usuario } from "@/lib/api";

const RUTAS_INTERNAS: Record<string, string> = {
  administrador: "/admin",
  ejecutivo: "/ejecutivo",
  operador_logistico: "/operador",
  analista_finanzas: "/analista",
};

export function Navbar() {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cantidadCarrito, setCantidadCarrito] = useState(0);
  const [menuAbierto, setMenuAbierto] = useState(false);

  useEffect(() => {
    setUsuario(getAuth().usuario);
    setCantidadCarrito(carrito.cantidadItems());
    const refresh = () => setCantidadCarrito(carrito.cantidadItems());
    window.addEventListener("carrito-actualizado", refresh);
    return () => window.removeEventListener("carrito-actualizado", refresh);
  }, []);

  const logout = () => {
    clearAuth();
    setUsuario(null);
    router.push("/");
  };

  const esCliente = usuario && (usuario.rol === "cliente_institucion" || usuario.rol === "cliente_paciente");
  const rutaInterna = usuario ? RUTAS_INTERNAS[usuario.rol] : null;

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-ink">MEDISTOCK</span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            <Link href="/catalogo" className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-primary-700">
              Catálogo
            </Link>
            {esCliente && (
              <Link href="/mis-pedidos" className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-primary-700">
                Mis pedidos
              </Link>
            )}
            {rutaInterna && (
              <Link href={rutaInterna} className="px-3 py-2 text-sm font-medium text-primary-700 hover:text-primary-900">
                Panel interno
              </Link>
            )}
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/carrito" className="relative p-2 text-slate-600 hover:text-primary-700">
              <ShoppingCart className="h-5 w-5" />
              {cantidadCarrito > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary-600 text-xs font-bold text-white">
                  {cantidadCarrito}
                </span>
              )}
            </Link>
            {usuario ? (
              <div className="hidden md:flex items-center gap-3">
                <div className="text-right">
                  <div className="text-sm font-semibold text-ink">{usuario.nombre}</div>
                  <div className="text-xs text-slate-500">{usuario.rol.replace(/_/g, " ")}</div>
                </div>
                <button onClick={logout} className="rounded-full p-2 text-slate-500 hover:bg-slate-100" title="Cerrar sesión">
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <Link href="/login" className="hidden md:flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700">
                <User className="h-4 w-4" /> Ingresar
              </Link>
            )}
            <button onClick={() => setMenuAbierto(!menuAbierto)} className="md:hidden p-2 text-slate-600">
              {menuAbierto ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {menuAbierto && (
          <div className="md:hidden border-t border-slate-200 py-3 space-y-2">
            <Link href="/catalogo" className="block px-2 py-2 text-sm font-medium text-slate-700">Catálogo</Link>
            {esCliente && <Link href="/mis-pedidos" className="block px-2 py-2 text-sm">Mis pedidos</Link>}
            {rutaInterna && <Link href={rutaInterna} className="block px-2 py-2 text-sm">Panel interno</Link>}
            {usuario ? (
              <button onClick={logout} className="block w-full text-left px-2 py-2 text-sm text-red-600">Cerrar sesión ({usuario.nombre})</button>
            ) : (
              <Link href="/login" className="block px-2 py-2 text-sm font-semibold text-primary-700">Ingresar</Link>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
