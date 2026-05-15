"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, Clock, Package } from "lucide-react";

export default function CheckoutExitoPage() {
  const params = useSearchParams();
  const orden = params.get("orden");
  const pendiente = params.get("pendiente") === "1";

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 text-center">
      <div className="flex justify-center mb-4">
        {pendiente ? (
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-amber-100">
            <Clock className="h-8 w-8 text-amber-600" />
          </div>
        ) : (
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
            <CheckCircle2 className="h-8 w-8 text-emerald-600" />
          </div>
        )}
      </div>

      <h1 className="text-3xl font-bold text-ink">
        {pendiente ? "Pedido recibido" : "¡Pago exitoso!"}
      </h1>

      <p className="mt-3 text-slate-600">
        {pendiente
          ? "Tu orden está pendiente de aprobación por un ejecutivo de cuentas."
          : "Tu pedido fue procesado correctamente."}
      </p>

      {orden && (
        <div className="mt-6 inline-block rounded-lg bg-slate-100 px-4 py-2">
          <span className="text-sm text-slate-600">Número de orden:</span>{" "}
          <span className="font-mono font-bold text-ink">{orden}</span>
        </div>
      )}

      <div className="mt-8 card text-left">
        <h2 className="font-semibold text-ink mb-3 flex items-center gap-2">
          <Package className="h-5 w-5 text-primary-600" /> ¿Qué sigue?
        </h2>
        <ol className="space-y-2 text-sm text-slate-700 list-decimal list-inside">
          {pendiente ? (
            <>
              <li>Un ejecutivo revisará tu pedido en las próximas horas hábiles.</li>
              <li>Te enviaremos un email con la confirmación y opciones de pago.</li>
              <li>Una vez pagado, prepararemos y despacharemos los productos.</li>
            </>
          ) : (
            <>
              <li>Recibirás un email de confirmación.</li>
              <li>Nuestro equipo logístico preparará tu pedido.</li>
              <li>Te enviaremos el código de seguimiento cuando salga a despacho.</li>
            </>
          )}
        </ol>
      </div>

      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <Link href="/mis-pedidos" className="btn-primary">Ver mis pedidos</Link>
        <Link href="/catalogo" className="btn-secondary">Seguir comprando</Link>
      </div>
    </div>
  );
}
