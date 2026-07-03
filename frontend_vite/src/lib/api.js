import Cookies from "js-cookie";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}, requireAuth = false) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (requireAuth) {
    const token = Cookies.get("medistock_token");
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new ApiError(errorData.detail || `Error ${res.status}`, res.status);
  }

  if (res.status === 204) return undefined;
  return res.json();
}

export const api = {
  get: (path, auth = false) => request(path, { method: "GET" }, auth),
  post: (path, body, auth = false) =>
    request(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }, auth),
  put: (path, body, auth = true) =>
    request(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }, auth),
  delete: (path, auth = true) => request(path, { method: "DELETE" }, auth),
};

// ============== Auth helpers ==============
export function saveAuth(token, usuario) {
  Cookies.set("medistock_token", token, { expires: 1 });
  Cookies.set("medistock_user", JSON.stringify(usuario), { expires: 1 });
}

export function getAuth() {
  const token = Cookies.get("medistock_token") || null;
  const userStr = Cookies.get("medistock_user");
  return { token, usuario: userStr ? JSON.parse(userStr) : null };
}

export function clearAuth() {
  Cookies.remove("medistock_token");
  Cookies.remove("medistock_user");
}

export const formatCLP = (n) =>
  new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(n);
