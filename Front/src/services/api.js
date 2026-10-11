import { supabase } from "../lib/supabase";

export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";
// Clave compartida de la API. Viaja en el bundle, por lo que NO es un secreto:
// la identidad real del usuario se acredita con su access token de Supabase.
const API_KEY = import.meta.env.VITE_BACKEND_API_KEY;

async function buildHeaders(extraHeaders = {}, { requireSession = true } = {}) {
  const headers = { ...extraHeaders };
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  if (requireSession) {
    // getSession() renueva el access token con el refresh token si expiró
    const { data } = await supabase.auth.getSession();
    const token = data?.session?.access_token;
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

const BACKEND_DOWN_MESSAGE =
  "El servidor de análisis no está disponible en este momento (puede estar iniciando o con un error de despliegue). Intente nuevamente en unos minutos.";

async function handleResponse(response, defaultMessage) {
  if (!response.ok) {
    // 502/503/504 sin JSON: el backend (HuggingFace Space) está caído o iniciando
    if ([502, 503, 504].includes(response.status) &&
        !(response.headers.get("content-type") || "").includes("application/json")) {
      throw new Error(BACKEND_DOWN_MESSAGE);
    }
    if (response.status === 401) {
      throw new Error("Tu sesión expiró. Inicia sesión nuevamente.");
    }
    if (response.status === 429) {
      const retry = response.headers.get("Retry-After");
      throw new Error(
        `Demasiadas solicitudes. Intenta nuevamente${retry ? ` en ${retry} segundos` : " más tarde"}.`
      );
    }
    let message = defaultMessage;
    try {
      const data = await response.json();
      if (typeof data?.detail === "string") message = data.detail;
    } catch {
      // cuerpo no JSON: se usa el mensaje por defecto
    }
    throw new Error(message);
  }
  return response.json();
}

/**
 * Comprueba si el backend responde. Devuelve { ok, message }.
 * No requiere sesión ni API key (GET /).
 */
export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    const response = await fetch(`${API_URL}/`, { signal: controller.signal });
    clearTimeout(timer);
    if (response.ok) return { ok: true, message: "" };
    return { ok: false, message: BACKEND_DOWN_MESSAGE };
  } catch {
    return { ok: false, message: BACKEND_DOWN_MESSAGE };
  }
}

export async function captureInterfaceByUrl(url, credentials = null, maxPages = 10, signal = null, jobId = null) {
  const response = await fetch(`${API_URL}/capture/url`, {
    method: "POST",
    headers: await buildHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({ url, auth: credentials, max_pages: maxPages, job_id: jobId }),
    signal,
  });

  return handleResponse(response, "No se pudo capturar la interfaz desde la URL.");
}

export async function getCaptureProgress(jobId) {
  if (!jobId) return { logs: [] };
  const response = await fetch(`${API_URL}/capture/progress?job_id=${encodeURIComponent(jobId)}`, {
    method: "GET",
    headers: await buildHeaders(),
  });

  if (!response.ok) return { logs: [] };
  return response.json();
}

export async function uploadZip(file, signal = null) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/upload/zip`, {
    method: "POST",
    headers: await buildHeaders(),
    body: formData,
    signal,
  });

  return handleResponse(response, "No se pudo procesar el archivo ZIP.");
}

export async function replicateHtmlFromContent(htmlContent, url, cssCache = null, cssomStyles = null) {
  const response = await fetch(`${API_URL}/replicate/content`, {
    method: "POST",
    headers: await buildHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({
      html_content: htmlContent,
      url,
      css_cache: cssCache,
      cssom_styles: cssomStyles,
    }),
  });

  return handleResponse(response, "No se pudo generar la réplica HTML.");
}

// runtimeMetrics: métricas medidas por Playwright sobre la página original
// characteristics: subconjunto priorizado de características; null = todas
export async function evaluateHtml(html, runtimeMetrics = null, characteristics = null) {
  const response = await fetch(`${API_URL}/evaluate/iso`, {
    method: "POST",
    headers: await buildHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({
      html,
      runtime_metrics: runtimeMetrics && Object.keys(runtimeMetrics).length ? runtimeMetrics : null,
      characteristics,
    }),
  });

  return handleResponse(response, "No se pudo evaluar el HTML.");
}

// El usuario se identifica en el backend a partir del token de sesión;
// ya no se envía user_id desde el cliente.
export async function generateReport(evaluation) {
  const response = await fetch(`${API_URL}/report/generate`, {
    method: "POST",
    headers: await buildHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({ evaluation }),
  });

  return handleResponse(response, "No se pudo generar el reporte técnico.");
}

export async function verifyEmail(email) {
  // Se llama antes del registro: no hay sesión todavía.
  const response = await fetch(`${API_URL}/auth/verify-email`, {
    method: "POST",
    headers: await buildHeaders(
      { "Content-Type": "application/json" },
      { requireSession: false }
    ),
    body: JSON.stringify({ email }),
  });

  return handleResponse(response, "No se pudo verificar el correo.");
}
