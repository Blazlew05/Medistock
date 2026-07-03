import { CheckCircle2, Clock, DollarSign, Edit2, Package, Plus, ShoppingBag, Truck, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { AuthGuard } from "../components/AuthGuard";
import { api, formatCLP } from "../lib/api";

const COLOR_CLASSES = {
  primary: "bg-primary-50 text-primary-600",
  blue: "bg-blue-50 text-blue-600",
  indigo: "bg-indigo-50 text-indigo-600",
  amber: "bg-amber-50 text-amber-600",
  emerald: "bg-emerald-50 text-emerald-600",
};

const CATEGORIAS = ["Material Descartable", "Equipamiento", "Soluciones", "Fármacos", "Procedimientos"];

export default function AdminPanel() {
  return (
    <AuthGuard rolesPermitidos={["administrador"]}>
      {() => <AdminLayout />}
    </AuthGuard>
  );
}

function AdminLayout() {
  const [tab, setTab] = useState("dashboard");

  return (
    <div className="mx-auto max-w-7xl px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-ink">Panel de administración</h1>
          <p className="text-slate-600">Gestión completa del sistema</p>
        </div>
      </div>

      <div className="flex gap-2 border-b border-slate-200 mb-6 overflow-x-auto">
        {["dashboard", "productos", "ordenes"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-3 text-sm font-semibold border-b-2 transition whitespace-nowrap ${
              tab === t ? "border-primary-600 text-primary-700" : "border-transparent text-slate-600 hover:text-ink"
            }`}
          >
            {t === "dashboard" && "Dashboard"}
            {t === "productos" && "Productos"}
            {t === "ordenes" && "Órdenes"}
          </button>
        ))}
      </div>

      {tab === "dashboard" && <DashboardTab />}
      {tab === "productos" && <ProductosTab />}
      {tab === "ordenes" && <OrdenesTab />}
    </div>
  );
}

function DashboardTab() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/api/v1/admin/dashboard", true).then(setData).catch(() => {});
  }, []);

  if (!data) return <div className="text-slate-500">Cargando...</div>;

  const cards = [
    { label: "Productos", value: data.total_productos, icon: Package, color: "primary" },
    { label: "Clientes", value: data.total_clientes, icon: Users, color: "blue" },
    { label: "Órdenes totales", value: data.total_ordenes, icon: ShoppingBag, color: "indigo" },
    { label: "Pendientes pago", value: data.ordenes_pendientes_pago, icon: Clock, color: "amber" },
    { label: "En preparación", value: data.ordenes_en_preparacion, icon: Package, color: "indigo" },
    { label: "Despachadas", value: data.ordenes_despachadas, icon: Truck, color: "primary" },
    { label: "Pagos aprobados", value: data.pagos_aprobados, icon: CheckCircle2, color: "emerald" },
    { label: "Total aprobado", value: formatCLP(data.monto_total_aprobado), icon: DollarSign, color: "emerald" },
  ];

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((c) => (
        <div key={c.label} className="card">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${COLOR_CLASSES[c.color]} mb-3`}>
            <c.icon className="h-5 w-5" />
          </div>
          <div className="text-sm text-slate-600">{c.label}</div>
          <div className="text-2xl font-bold text-ink mt-1">{c.value}</div>
        </div>
      ))}
    </div>
  );
}

function ProductosTab() {
  const [productos, setProductos] = useState([]);
  const [editando, setEditando] = useState(null);
  const [creando, setCreando] = useState(false);

  function cargar() {
    api.get("/api/v1/admin/productos", true).then(setProductos).catch(() => {});
  }

  useEffect(() => { cargar(); }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-slate-600">{productos.length} productos</p>
        <button onClick={() => setCreando(true)} className="btn-primary">
          <Plus className="h-4 w-4" /> Nuevo producto
        </button>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-slate-600 border-b border-slate-200">
            <tr>
              <th className="pb-3 font-semibold">Código</th>
              <th className="pb-3 font-semibold">Nombre</th>
              <th className="pb-3 font-semibold">Categoría</th>
              <th className="pb-3 font-semibold text-right">Precio</th>
              <th className="pb-3 font-semibold text-right">Stock</th>
              <th className="pb-3 font-semibold">Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {productos.map((p) => (
              <tr key={p.id} className="border-b border-slate-100">
                <td className="py-3 font-mono text-xs">{p.codigo}</td>
                <td className="py-3 font-medium">{p.nombre}</td>
                <td className="py-3 text-slate-600">{p.categoria}</td>
                <td className="py-3 text-right">{formatCLP(p.precio)}</td>
                <td className="py-3 text-right">{p.stock_total}</td>
                <td className="py-3">
                  <span className={`badge ${p.activo ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-600"}`}>
                    {p.activo ? "Activo" : "Inactivo"}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button onClick={() => setEditando(p)} className="text-primary-600 hover:text-primary-800 p-1">
                    <Edit2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(editando || creando) && (
        <ProductoForm
          producto={editando}
          onClose={() => { setEditando(null); setCreando(false); }}
          onSaved={() => { setEditando(null); setCreando(false); cargar(); }}
        />
      )}
    </div>
  );
}

function ProductoForm({ producto, onClose, onSaved }) {
  const [form, setForm] = useState({
    codigo: producto?.codigo || "",
    nombre: producto?.nombre || "",
    descripcion: producto?.descripcion || "",
    categoria: producto?.categoria || "Material Descartable",
    precio: producto?.precio || 0,
    unidad: producto?.unidad || "unidad",
    requiere_receta: producto?.requiere_receta || false,
    es_critico: producto?.es_critico || false,
    activo: producto?.activo ?? true,
  });
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  async function guardar(e) {
    e.preventDefault();
    setError("");
    setGuardando(true);
    try {
      if (producto) {
        await api.put(`/api/v1/admin/productos/${producto.id}`, form);
      } else {
        await api.post("/api/v1/admin/productos", form, true);
      }
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar");
      setGuardando(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-xl font-bold text-ink mb-4">
          {producto ? "Editar producto" : "Nuevo producto"}
        </h2>
        <form onSubmit={guardar} className="space-y-4">
          {error && <div className="rounded bg-red-50 border border-red-200 p-3 text-sm text-red-800">{error}</div>}
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label">Código</label>
              <input className="input" required value={form.codigo} disabled={!!producto} onChange={(e) => setForm({ ...form, codigo: e.target.value })} />
            </div>
            <div>
              <label className="label">Categoría</label>
              <select className="input" value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })}>
                {CATEGORIAS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="label">Nombre</label>
            <input className="input" required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          </div>
          <div>
            <label className="label">Descripción</label>
            <textarea className="input" required rows={2} value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label">Precio (CLP)</label>
              <input type="number" className="input" required min={0} value={form.precio} onChange={(e) => setForm({ ...form, precio: parseInt(e.target.value) || 0 })} />
            </div>
            <div>
              <label className="label">Unidad</label>
              <input className="input" value={form.unidad} onChange={(e) => setForm({ ...form, unidad: e.target.value })} />
            </div>
          </div>
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.requiere_receta} onChange={(e) => setForm({ ...form, requiere_receta: e.target.checked })} /> Requiere receta
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.es_critico} onChange={(e) => setForm({ ...form, es_critico: e.target.checked })} /> Insumo crítico
            </label>
            {producto && (
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} /> Activo
              </label>
            )}
          </div>
          <div className="flex gap-2 justify-end pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">Cancelar</button>
            <button type="submit" disabled={guardando} className="btn-primary">{guardando ? "Guardando..." : "Guardar"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

function OrdenesTab() {
  const [ordenes, setOrdenes] = useState([]);

  useEffect(() => {
    api.get("/api/v1/admin/ordenes", true).then(setOrdenes).catch(() => {});
  }, []);

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="text-left text-slate-600 border-b border-slate-200">
          <tr>
            <th className="pb-3 font-semibold">Número</th>
            <th className="pb-3 font-semibold">Cliente</th>
            <th className="pb-3 font-semibold">Fecha</th>
            <th className="pb-3 font-semibold">Estado</th>
            <th className="pb-3 font-semibold">Urgencia</th>
            <th className="pb-3 font-semibold text-right">Total</th>
          </tr>
        </thead>
        <tbody>
          {ordenes.map((o) => (
            <tr key={o.id} className="border-b border-slate-100">
              <td className="py-3 font-mono text-xs">{o.numero}</td>
              <td className="py-3">#{o.cliente_id}</td>
              <td className="py-3 text-slate-600">{new Date(o.creada_en).toLocaleDateString("es-CL")}</td>
              <td className="py-3">{o.estado.replace(/_/g, " ")}</td>
              <td className="py-3">
                <span className={`badge ${o.urgencia === "alta" ? "bg-red-100 text-red-800" : o.urgencia === "media" ? "bg-amber-100 text-amber-800" : "bg-slate-100 text-slate-600"}`}>
                  {o.urgencia}
                </span>
              </td>
              <td className="py-3 text-right font-semibold">{formatCLP(o.total)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
