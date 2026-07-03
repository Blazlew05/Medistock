import { ArrowRight, ShoppingBag, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { formatCLP, getAuth } from "../lib/api";
import { carrito } from "../lib/carrito";

export default function Carrito() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [montado, setMontado] = useState(false);

  useEffect(() => {
    setItems(carrito.get());
    setMontado(true);
    const refresh = () => setItems(carrito.get());
    window.addEventListener("carrito-actualizado", refresh);
    return () => window.removeEventListener("carrito-actualizado", refresh);
  }, []);

  if (!montado) return null;

  const subtotal = items.reduce((acc, i) => acc + i.producto.precio * i.cantidad, 0);

  function irACheckout() {
    const { usuario } = getAuth();
    if (!usuario) {
      navigate("/login");
    } else {
      navigate("/checkout");
    }
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <ShoppingBag className="h-16 w-16 text-slate-300 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-ink">Tu carrito está vacío</h1>
        <p className="mt-2 text-slate-600">Agrega productos del catálogo para empezar.</p>
        <Link to="/catalogo" className="btn-primary mt-6">Ver catálogo</Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold text-ink mb-6">Tu carrito ({items.length})</h1>

      <div className="grid md:grid-cols-[1fr_320px] gap-6">
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.producto.codigo} className="card flex items-center gap-4">
              <div className="h-16 w-16 rounded-lg bg-slate-100 flex items-center justify-center text-slate-400 text-xs">
                IMG
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs text-slate-500 font-mono">{item.producto.codigo}</div>
                <Link to={`/producto/${item.producto.codigo}`} className="font-semibold text-ink line-clamp-1 hover:text-primary-700">
                  {item.producto.nombre}
                </Link>
                <div className="text-sm text-slate-600">{formatCLP(item.producto.precio)} / {item.producto.unidad}</div>
              </div>
              <div className="flex items-center">
                <button onClick={() => carrito.cambiarCantidad(item.producto.codigo, item.cantidad - 1)} className="rounded-l-lg border border-slate-300 bg-white w-8 h-8 hover:bg-slate-50">-</button>
                <div className="w-10 h-8 border-y border-slate-300 flex items-center justify-center text-sm bg-white">{item.cantidad}</div>
                <button onClick={() => carrito.cambiarCantidad(item.producto.codigo, item.cantidad + 1)} className="rounded-r-lg border border-slate-300 bg-white w-8 h-8 hover:bg-slate-50">+</button>
              </div>
              <div className="text-right min-w-[100px]">
                <div className="font-bold text-ink">{formatCLP(item.producto.precio * item.cantidad)}</div>
              </div>
              <button onClick={() => carrito.quitar(item.producto.codigo)} className="text-slate-400 hover:text-red-600 p-2">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>

        <aside className="card h-fit sticky top-20">
          <h2 className="font-semibold text-ink mb-4">Resumen</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-600">Subtotal</span><span className="font-semibold">{formatCLP(subtotal)}</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Despacho</span><span className="text-slate-500">Se calcula en checkout</span></div>
          </div>
          <div className="border-t border-slate-200 mt-3 pt-3 flex justify-between items-baseline">
            <span className="font-semibold text-ink">Total estimado</span>
            <span className="text-2xl font-bold text-ink">{formatCLP(subtotal)}</span>
          </div>
          <button onClick={irACheckout} className="btn-primary w-full mt-4">
            Ir a pagar <ArrowRight className="h-4 w-4" />
          </button>
          <button onClick={() => carrito.vaciar()} className="w-full mt-2 text-sm text-slate-500 hover:text-red-600">
            Vaciar carrito
          </button>
        </aside>
      </div>
    </div>
  );
}
