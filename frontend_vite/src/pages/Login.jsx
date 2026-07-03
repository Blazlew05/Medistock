import { Activity, AlertCircle } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, saveAuth } from "../lib/api";

const CUENTAS_DEMO = [
  { rol: "Administrador", email: "admin@medistock.cl", pass: "admin123" },
  { rol: "Ejecutivo", email: "ejecutivo@medistock.cl", pass: "ejec123" },
  { rol: "Operador", email: "operador@medistock.cl", pass: "oper123" },
  { rol: "Analista", email: "analista@medistock.cl", pass: "anal123" },
  { rol: "Institución", email: "compras@clinicalasandes.cl", pass: "clinica123" },
  { rol: "Paciente", email: "paciente@gmail.com", pass: "paciente123" },
];

const RUTAS = {
  administrador: "/admin",
  ejecutivo: "/ejecutivo",
  operador_logistico: "/operador",
  analista_finanzas: "/analista",
  cliente_institucion: "/catalogo",
  cliente_paciente: "/catalogo",
};

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setCargando(true);
    try {
      const res = await api.post("/api/v1/auth/login", { email, password });
      saveAuth(res.access_token, res.usuario);
      navigate(RUTAS[res.usuario.rol] || "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al iniciar sesión");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 grid md:grid-cols-2 gap-10 items-start">
      <div>
        <div className="flex items-center gap-2 mb-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-600">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-ink">Iniciar sesión</h1>
        </div>

        <form onSubmit={handleLogin} className="card space-y-4">
          {error && (
            <div className="flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" /> {error}
            </div>
          )}
          <div>
            <label className="label">Correo electrónico</label>
            <input type="email" className="input" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="tu@correo.cl" />
          </div>
          <div>
            <label className="label">Contraseña</label>
            <input type="password" className="input" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          </div>
          <button type="submit" disabled={cargando} className="btn-primary w-full">
            {cargando ? "Ingresando..." : "Ingresar"}
          </button>
          <div className="text-center text-sm text-slate-600">
            ¿No tienes cuenta? <Link to="/registro" className="font-semibold text-primary-700 hover:underline">Regístrate</Link>
          </div>
        </form>
      </div>

      <div className="card bg-slate-50 border-slate-200">
        <h2 className="font-semibold text-ink mb-2">Cuentas de demostración</h2>
        <p className="text-sm text-slate-600 mb-4">Haz clic para autocompletar las credenciales.</p>
        <div className="space-y-2">
          {CUENTAS_DEMO.map((c) => (
            <button
              key={c.email}
              type="button"
              onClick={() => { setEmail(c.email); setPassword(c.pass); }}
              className="w-full text-left rounded-lg border border-slate-200 bg-white p-3 hover:border-primary-400 transition"
            >
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-primary-700 uppercase tracking-wide">{c.rol}</div>
                <div className="text-xs text-slate-400 font-mono">{c.pass}</div>
              </div>
              <div className="text-sm font-medium text-ink mt-1">{c.email}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
