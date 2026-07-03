import { AlertCircle, CheckCircle2, CreditCard, Truck } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthGuard } from "../components/AuthGuard";
import { api, formatCLP } from "../lib/api";
import { carrito } from "../lib/carrito";

export default function Checkout() {
  return (
    <AuthGuard rolesPermitidos={["cliente_paciente", "cliente_institucion"]}>
      {(usuario) => <CheckoutForm usuario={usuario} />}
    </AuthGuard>
  );
}

function CheckoutForm({ usuario }) {
  const navigate = useNavigate();
  const formRef = useRef(null);
  const [items, setItems] = useState(carrito.get());
  const [tipoDespacho, setTipoDespacho] = useState("normal");
  const [urgencia, setUrgencia] = useState("media");
  const [direccion, setDireccion] = useState(usuario.direccion || "");
  const [notas, setNotas] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    if (carrito.get().length === 0) navigate("/carrito");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (items.some((i) => i.cantidad > i.producto.stock_total)) {
      setError("Algunos productos no tienen stock suficiente. Revisa tu carrito.");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const subtotal = items.reduce((acc, i) => acc + i.producto.precio * i.cantidad, 0);
  const costoEnvio = tipoDespacho === "express" ? 5990 : 2990;
  const total = subtotal + costoEnvio;
  const esInstitucion = usuario.rol === "cliente_institucion";

  async function crearOrdenYPagar(e, gateway) {
    e.preventDefault();
    if (formRef.current && !formRef.current.reportValidity()) return;

    setError("");
    setCargando(true);
    try {
      const orden = await api.post("/api/v1/ordenes", {
        items: items.map((i) => ({ producto_id: i.producto.id, cantidad: i.cantidad })),
        tipo_despacho: tipoDespacho,
        urgencia,
        direccion_envio: direccion,
        notas: notas || undefined,
      }, true);

      // Si es institución, no se paga aún (queda pendiente aprobación)
      if (esInstitucion) {
        carrito.vaciar();
        navigate(`/checkout/exito?orden=${orden.numero}&pendiente=1`);
        return;
      }

      if (gateway === "webpay") {
        const pago = await api.post(`/api/v1/pagos/webpay/iniciar/${orden.id}`, null, true);
        carrito.vaciar();
        const form = document.createElement("form");
        form.method = "POST";
        form.action = pago.url;
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "token_ws";
        input.value = pago.token;
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
        return;
      }

      const pago = await api.post(`/api/v1/pagos/iniciar/${orden.id}`, null, true);
      carrito.vaciar();
      const url = pago.sandbox_init_point || pago.init_point;
      window.location.href = url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al procesar el pedido");
      setCargando(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-3xl font-bold text-ink mb-6">Finalizar compra</h1>

      <form ref={formRef} className="grid md:grid-cols-[1fr_360px] gap-6">
        <div className="space-y-6">
          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800 flex gap-2">
              <AlertCircle className="h-4 w-4 mt-0.5" /> {error}
            </div>
          )}

          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <Truck className="h-5 w-5 text-primary-600" />
              <h2 className="font-semibold text-ink">Datos de despacho</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="label">Dirección de entrega</label>
                <input className="input" required value={direccion} onChange={(e) => setDireccion(e.target.value)} placeholder="Calle, número, comuna" />
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="label">Tipo de despacho</label>
                  <select className="input" value={tipoDespacho} onChange={(e) => setTipoDespacho(e.target.value)}>
                    <option value="normal">Normal · 72h · {formatCLP(2990)}</option>
                    <option value="express">Express · 24h RM · {formatCLP(5990)}</option>
                  </select>
                </div>
                <div>
                  <label className="label">Urgencia médica</label>
                  <select className="input" value={urgencia} onChange={(e) => setUrgencia(e.target.value)}>
                    <option value="baja">Baja</option>
                    <option value="media">Media</option>
                    <option value="alta">Alta (caso crítico)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Notas (opcional)</label>
                <textarea className="input" rows={2} value={notas} onChange={(e) => setNotas(e.target.value)} placeholder="Información adicional para el repartidor..." />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-2 mb-3">
              <CreditCard className="h-5 w-5 text-primary-600" />
              <h2 className="font-semibold text-ink">Forma de pago</h2>
            </div>
            {esInstitucion ? (
              <div className="rounded-lg bg-amber-50 border border-amber-200 p-3 text-sm text-amber-900">
                <strong>Cuenta institucional:</strong> tu orden quedará pendiente de aprobación
                por un ejecutivo de cuentas antes de proceder al pago. Te contactaremos vía email
                con las opciones (transferencia, MercadoPago o Webpay Plus).
              </div>
            ) : (
              <div className="rounded-lg bg-primary-50 border border-primary-200 p-3 text-sm">
                <div className="font-semibold text-primary-900">MercadoPago o Webpay Plus</div>
                <div className="text-primary-700 mt-1">
                  Elige la pasarela con la que quieras pagar. Serás redirigido para completar el
                  pago con tarjeta de crédito, débito o efectivo (Servipag/Multicaja).
                </div>
              </div>
            )}
          </div>
        </div>

        <aside className="card h-fit sticky top-20">
          <h2 className="font-semibold text-ink mb-4">Tu pedido</h2>
          <div className="space-y-2 max-h-60 overflow-y-auto mb-4 pr-1">
            {items.map((i) => (
              <div key={i.producto.codigo} className="flex justify-between text-sm">
                <div className="flex-1 min-w-0">
                  <div className="text-ink line-clamp-1">{i.producto.nombre}</div>
                  <div className="text-xs text-slate-500">× {i.cantidad}</div>
                </div>
                <div className="font-medium text-ink ml-2">{formatCLP(i.producto.precio * i.cantidad)}</div>
              </div>
            ))}
          </div>
          <div className="space-y-2 text-sm border-t border-slate-200 pt-3">
            <div className="flex justify-between"><span className="text-slate-600">Subtotal</span><span>{formatCLP(subtotal)}</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Despacho</span><span>{formatCLP(costoEnvio)}</span></div>
            <div className="flex justify-between items-baseline pt-2 border-t border-slate-200">
              <span className="font-semibold text-ink">Total</span>
              <span className="text-2xl font-bold text-ink">{formatCLP(total)}</span>
            </div>
          </div>

          {esInstitucion ? (
            <button type="button" disabled={cargando} onClick={(e) => crearOrdenYPagar(e, null)} className="btn-primary w-full mt-4 py-3">
              {cargando ? "Procesando..." : "Enviar para aprobación"}
            </button>
          ) : (
            <div className="mt-4 space-y-2">
              <button type="button" disabled={cargando} onClick={(e) => crearOrdenYPagar(e, "mercadopago")} className="btn-primary w-full py-3">
                {cargando ? "Procesando..." : "Pagar con MercadoPago"}
              </button>
              <button type="button" disabled={cargando} onClick={(e) => crearOrdenYPagar(e, "webpay")} className="btn-secondary w-full py-3">
                {cargando ? "Procesando..." : "Pagar con Webpay Plus"}
              </button>
            </div>
          )}

          <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" /> Pago seguro · Productos certificados
          </div>
        </aside>
      </form>
    </div>
  );
}
