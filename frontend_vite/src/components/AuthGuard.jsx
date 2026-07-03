import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAuth } from "../lib/api";

export function AuthGuard({ rolesPermitidos, children }) {
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState(null);
  const [verificando, setVerificando] = useState(true);

  useEffect(() => {
    const { token, usuario: u } = getAuth();
    if (!token || !u) {
      navigate("/login");
      return;
    }
    if (!rolesPermitidos.includes(u.rol)) {
      navigate("/");
      return;
    }
    setUsuario(u);
    setVerificando(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (verificando || !usuario) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-sm text-slate-500">Verificando acceso...</div>
      </div>
    );
  }

  return <>{children(usuario)}</>;
}
