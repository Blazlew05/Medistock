import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, saveAuth } from "../lib/api";

export default function Registro() {
  const navigate = useNavigate();
  const [rol, setRol] = useState("cliente_paciente");
  const [form, setForm] = useState({
    nombre: "", email: "", password: "", empresa: "", rut: "", telefono: "", direccion: "",
  });
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function handleRegistro(e) {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      await api.post("/api/v1/auth/registro", { ...form, rol });
      const res = await api.post("/api/v1/auth/login", { email: form.email, password: form.password });
      saveAuth(res.access_token, res.usuario);
      navigate("/catalogo");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al registrarse");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-bold text-ink mb-1">Crear cuenta</h1>
      <p className="text-slate-600 mb-6">¿Eres paciente o representas una institución?</p>

      <div className="flex gap-2 mb-6">
        {["cliente_paciente", "cliente_institucion"].map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setRol(r)}
            className={`flex-1 rounded-lg border p-4 text-left transition ${
              rol === r ? "border-primary-500 bg-primary-50" : "border-slate-200 bg-white hover:border-slate-300"
            }`}
          >
            <div className="font-semibold text-ink">{r === "cliente_paciente" ? "Paciente" : "Institución"}</div>
            <div className="text-xs text-slate-600 mt-1">
              {r === "cliente_paciente" ? "Compras para uso personal o domiciliario" : "Clínica, hospital u organización"}
            </div>
          </button>
        ))}
      </div>

      <form onSubmit={handleRegistro} className="card space-y-4">
        {error && <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">{error}</div>}
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="label">Nombre completo</label>
            <input className="input" required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          </div>
          <div>
            <label className="label">RUT</label>
            <input className="input" value={form.rut} onChange={(e) => setForm({ ...form, rut: e.target.value })} placeholder="12.345.678-9" />
          </div>
        </div>
        {rol === "cliente_institucion" && (
          <div>
            <label className="label">Empresa / Institución</label>
            <input className="input" required value={form.empresa} onChange={(e) => setForm({ ...form, empresa: e.target.value })} />
          </div>
        )}
        <div>
          <label className="label">Correo electrónico</label>
          <input type="email" className="input" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="label">Contraseña (mín. 6)</label>
            <input type="password" className="input" required minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
          <div>
            <label className="label">Teléfono</label>
            <input className="input" value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} placeholder="+56 9 ..." />
          </div>
        </div>
        <div>
          <label className="label">Dirección de despacho</label>
          <input className="input" value={form.direccion} onChange={(e) => setForm({ ...form, direccion: e.target.value })} />
        </div>
        <button type="submit" disabled={cargando} className="btn-primary w-full">
          {cargando ? "Creando cuenta..." : "Crear cuenta"}
        </button>
        <div className="text-center text-sm text-slate-600">
          ¿Ya tienes cuenta? <Link to="/login" className="font-semibold text-primary-700 hover:underline">Inicia sesión</Link>
        </div>
      </form>
    </div>
  );
}
