export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8086";

async function handleResponse(response, defaultMessage) {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || defaultMessage);
  }

  return response.json();
}

export async function captureInterfaceByUrl(url, credentials = null) {
  const response = await fetch(`${API_URL}/capture/url`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url, auth: credentials }),
  });

  return handleResponse(response, "No se pudo capturar la interfaz desde la URL.");
}

export async function uploadZip(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/upload/zip`, {
    method: "POST",
    body: formData,
  });

  return handleResponse(response, "No se pudo procesar el archivo ZIP.");
}

export async function replicateHtmlFromContent(htmlContent, url, cssCache = null, cssomStyles = null) {
  const response = await fetch(`${API_URL}/replicate/content`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      html_content: htmlContent,
      url,
      css_cache: cssCache,
      cssom_styles: cssomStyles,
    }),
  });

  return handleResponse(response, "No se pudo generar la réplica HTML.");
}

export async function evaluateHtml(html) {
  const response = await fetch(`${API_URL}/evaluate/iso`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ html }),
  });

  return handleResponse(response, "No se pudo evaluar el HTML.");
}

export async function generateReport(evaluation, userId = null) {
  const response = await fetch(`${API_URL}/report/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ 
      evaluation,
      user_id: userId
    }),
  });

  return handleResponse(response, "No se pudo generar el reporte técnico.");
}