"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getAuth, type RolUsuario, type Usuario } from "@/lib/api";

export function AuthGuard({
  rolesPermitidos,
  children,
}: {
  rolesPermitidos: RolUsuario[];
  children: (usuario: Usuario) => React.ReactNode;
}) {
  const router = useRouter();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [verificando, setVerificando] = useState(true);

  useEffect(() => {
    const { token, usuario: u } = getAuth();
    if (!token || !u) {
      router.push("/login");
      return;
    }
    if (!rolesPermitidos.includes(u.rol)) {
      router.push("/");
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
