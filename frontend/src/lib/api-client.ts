/* Cliente HTTP para comunicación directa con el backend FastAPI de AlToque AI. */

const CLAVE_API_URL = "altoque_api_url";
const URL_POR_DEFECTO = "http://localhost:8000";

export function obtenerUrlApi(): string {
  return localStorage.getItem(CLAVE_API_URL) || URL_POR_DEFECTO;
}

export function guardarUrlApi(url: string) {
  localStorage.setItem(CLAVE_API_URL, url.replace(/\/+$/, ""));
}

/* Token JWT almacenado en localStorage */
const CLAVE_TOKEN = "altoque_token";

export function obtenerToken(): string | null {
  return localStorage.getItem(CLAVE_TOKEN);
}

export function guardarToken(token: string) {
  localStorage.setItem(CLAVE_TOKEN, token);
}

export function borrarToken() {
  localStorage.removeItem(CLAVE_TOKEN);
}

export type UsuarioBackend = {
  id: string;
  email: string;
  full_name: string;
  role: "patient" | "caregiver" | "doctor";
  is_active: boolean;
};

/* Función genérica para peticiones al backend */
export async function peticionApi<T = unknown>(
  ruta: string,
  opciones: RequestInit = {}
): Promise<T> {
  const base = obtenerUrlApi();
  const url = `${base}${ruta}`;
  const token = obtenerToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((opciones.headers as Record<string, string>) || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(url, { ...opciones, headers });
  if (resp.status === 401) {
    borrarToken();
    throw new Error("Sesión expirada o credenciales inválidas");
  }

  let body: any = null;
  const contentType = resp.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    body = await resp.json();
  }

  if (!resp.ok) {
    const errorMsg =
      body?.detail ||
      (Array.isArray(body?.detail) ? body.detail.map((d: any) => d.msg).join(", ") : null) ||
      `Error del servidor (${resp.status})`;
    throw new Error(errorMsg);
  }

  return body as T;
}

/* Verificación de salud del backend */
export async function verificarConexion(): Promise<boolean> {
  try {
    const datos = await peticionApi<{ status: string }>("/health");
    return datos?.status === "healthy";
  } catch {
    return false;
  }
}

/* Autenticación real contra el backend FastAPI */
export async function iniciarSesion(
  email: string,
  password: string
): Promise<{ token: string; user: UsuarioBackend }> {
  const tokenResp = await peticionApi<{
    access_token: string;
    refresh_token: string;
    token_type: string;
  }>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  guardarToken(tokenResp.access_token);

  // Obtener perfil real del usuario recién autenticado
  const user = await peticionApi<UsuarioBackend>("/api/v1/auth/me");
  return { token: tokenResp.access_token, user };
}

export async function registrarUsuario(
  email: string,
  password: string,
  full_name: string,
  role: "patient" | "caregiver"
): Promise<{ token: string; user: UsuarioBackend }> {
  await peticionApi<UsuarioBackend>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
      full_name,
      role,
    }),
  });

  // Autenticar de inmediato tras registro exitoso
  return await iniciarSesion(email, password);
}

export async function cerrarSesion() {
  borrarToken();
}
