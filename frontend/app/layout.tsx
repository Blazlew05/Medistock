import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/componentes/Navbar";

export const metadata: Metadata = {
  title: "MEDISTOCK - Insumos clínicos a tiempo",
  description: "Distribuidora de insumos y equipamiento clínico para Chile",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-6">
          <div className="mx-auto max-w-7xl px-4 text-center text-sm text-slate-500">
            © 2026 MEDISTOCK · Distribución de insumos y equipamiento clínico
          </div>
        </footer>
      </body>
    </html>
  );
}
