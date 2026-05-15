import Link from "next/link";
import { ShieldCheck, Truck, Clock, Package, ArrowRight, Heart, Stethoscope, Pill } from "lucide-react";

export default function Home() {
  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-700 via-primary-800 to-ink">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
          backgroundSize: "32px 32px",
        }} />
        <div className="relative mx-auto max-w-7xl px-4 py-20 md:py-28">
          <div className="grid gap-12 md:grid-cols-2 items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-primary-300/30 bg-primary-500/10 px-3 py-1 text-xs font-semibold text-primary-200">
                <Heart className="h-3 w-3" /> Más de 20 años abasteciendo a Chile
              </div>
              <h1 className="mt-5 text-4xl md:text-5xl lg:text-6xl font-bold text-white tracking-tight">
                Insumos clínicos cuando<br />
                <span className="text-primary-300">cada minuto cuenta</span>
              </h1>
              <p className="mt-5 text-lg text-primary-100 max-w-lg">
                Distribuidora MEDISTOCK abastece a clínicas, hospitales y pacientes con
                hospitalización domiciliaria desde 5 centros logísticos a lo largo del país.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link href="/catalogo" className="inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 font-semibold text-primary-800 hover:bg-primary-50">
                  Ver catálogo <ArrowRight className="h-4 w-4" />
                </Link>
                <Link href="/registro" className="inline-flex items-center gap-2 rounded-lg border border-white/30 bg-white/10 px-6 py-3 font-semibold text-white hover:bg-white/20">
                  Soy una institución
                </Link>
              </div>
            </div>
            <div className="hidden md:grid grid-cols-2 gap-4">
              {[
                { icon: ShieldCheck, t: "Productos certificados", s: "ISO 13485 · MINSAL" },
                { icon: Truck, t: "Despacho express", s: "24h en RM" },
                { icon: Clock, t: "Stock en tiempo real", s: "API para tu ERP" },
                { icon: Package, t: "5 centros logísticos", s: "Norte, RM, Sur" },
              ].map((f, i) => (
                <div key={i} className="rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 p-5 text-white">
                  <f.icon className="h-7 w-7 text-primary-300 mb-3" />
                  <div className="font-semibold">{f.t}</div>
                  <div className="text-sm text-primary-100 mt-1">{f.s}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CATEGORIAS */}
      <section className="mx-auto max-w-7xl px-4 py-16">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-ink">Categorías principales</h2>
          <p className="mt-3 text-slate-600">Todo el surtido clínico que tu institución necesita, en un solo lugar.</p>
        </div>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            { icon: Package, n: "Material Descartable", d: "Jeringas, guantes, gasas, mascarillas" },
            { icon: Stethoscope, n: "Equipamiento", d: "Monitores, oxímetros, tensiómetros" },
            { icon: Pill, n: "Fármacos y soluciones", d: "Medicamentos, sueros, antisépticos" },
          ].map((c) => (
            <Link key={c.n} href={`/catalogo?categoria=${encodeURIComponent(c.n)}`} className="group rounded-xl border border-slate-200 bg-white p-6 hover:border-primary-500 hover:shadow-lg transition">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-50 text-primary-600 group-hover:bg-primary-100">
                <c.icon className="h-6 w-6" />
              </div>
              <h3 className="mt-4 font-semibold text-ink">{c.n}</h3>
              <p className="mt-1 text-sm text-slate-600">{c.d}</p>
              <div className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-primary-700">
                Ver productos <ArrowRight className="h-3 w-3" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* B2B/B2C SPLIT */}
      <section className="bg-slate-50 border-y border-slate-200">
        <div className="mx-auto max-w-7xl px-4 py-16 grid md:grid-cols-2 gap-8">
          <div className="rounded-2xl bg-white border border-slate-200 p-8">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700">PARA INSTITUCIONES</div>
            <h3 className="mt-4 text-2xl font-bold text-ink">Clínicas y hospitales</h3>
            <p className="mt-3 text-slate-600">Integra tu ERP con nuestra API REST para consultar catálogo, precios y stock en tiempo real. Sin más planillas Excel.</p>
            <Link href="/registro" className="mt-6 inline-flex btn-primary">Crear cuenta institucional</Link>
          </div>
          <div className="rounded-2xl bg-white border border-slate-200 p-8">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700">PARA PACIENTES</div>
            <h3 className="mt-4 text-2xl font-bold text-ink">Hospitalización domiciliaria</h3>
            <p className="mt-3 text-slate-600">Compra los insumos que tu equipo médico te indicó. Despacho express en RM con pago seguro vía MercadoPago.</p>
            <Link href="/catalogo" className="mt-6 inline-flex btn-primary">Ver productos</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
