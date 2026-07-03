import { Route, Routes } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import AdminPanel from "./pages/AdminPanel";
import AnalistaPanel from "./pages/AnalistaPanel";
import Carrito from "./pages/Carrito";
import Catalogo from "./pages/Catalogo";
import Checkout from "./pages/Checkout";
import CheckoutExito from "./pages/CheckoutExito";
import EjecutivoPanel from "./pages/EjecutivoPanel";
import Home from "./pages/Home";
import Login from "./pages/Login";
import MisPedidos from "./pages/MisPedidos";
import OperadorPanel from "./pages/OperadorPanel";
import ProductoDetalle from "./pages/ProductoDetalle";
import Registro from "./pages/Registro";

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Registro />} />
          <Route path="/catalogo" element={<Catalogo />} />
          <Route path="/producto/:codigo" element={<ProductoDetalle />} />
          <Route path="/carrito" element={<Carrito />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/checkout/exito" element={<CheckoutExito />} />
          <Route path="/mis-pedidos" element={<MisPedidos />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/ejecutivo" element={<EjecutivoPanel />} />
          <Route path="/operador" element={<OperadorPanel />} />
          <Route path="/analista" element={<AnalistaPanel />} />
        </Routes>
      </main>
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="mx-auto max-w-7xl px-4 text-center text-sm text-slate-500">
          © 2026 MEDISTOCK · Distribución de insumos y equipamiento clínico
        </div>
      </footer>
    </div>
  );
}

export default App;
