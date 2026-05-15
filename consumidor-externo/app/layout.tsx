import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Farmacia Cruz Amarilla - Catálogo en línea",
  description: "Tu farmacia de confianza desde 1985. Catálogo en tiempo real.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen flex flex-col">
        <header className="bg-amarilla-500 border-b-4 border-amarilla-700">
          <div className="mx-auto max-w-7xl px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-white rounded-lg p-1.5">
                <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7">
                  <path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7V3z" fill="#a16207" />
                </svg>
              </div>
              <div>
                <div className="font-extrabold text-amarilla-900 leading-tight tracking-tight text-lg">FARMACIA</div>
                <div className="font-bold text-amarilla-800 leading-tight tracking-wider text-sm -mt-1">CRUZ AMARILLA</div>
              </div>
            </div>
            <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-amarilla-900">
              <a href="/">Inicio</a>
              <a href="/catalogo">Catálogo</a>
              <a href="#sucursales">Sucursales</a>
              <a href="#contacto">Contacto</a>
            </nav>
            <div className="flex items-center gap-2 text-xs">
              <span className="bg-amarilla-900 text-amarilla-100 px-2 py-1 rounded font-mono">
                🟢 LIVE - Stock en tiempo real
              </span>
            </div>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer id="contacto" className="bg-amarilla-900 text-amarilla-100 py-8">
          <div className="mx-auto max-w-7xl px-4 grid sm:grid-cols-3 gap-6 text-sm">
            <div>
              <div className="font-bold text-amarilla-50 mb-2">Cruz Amarilla S.A.</div>
              <p>Tu farmacia de confianza desde 1985. 47 sucursales en todo Chile.</p>
            </div>
            <div id="sucursales">
              <div className="font-bold text-amarilla-50 mb-2">Sucursales</div>
              <p>Santiago · Valparaíso · Concepción · Temuco · Antofagasta</p>
            </div>
            <div>
              <div className="font-bold text-amarilla-50 mb-2">Contacto</div>
              <p>📞 600 600 1234<br />✉️ contacto@cruzamarilla.cl</p>
              <p className="mt-3 text-xs opacity-75">
                Sitio de demostración. Catálogo provisto por <strong>MEDISTOCK API</strong>.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
