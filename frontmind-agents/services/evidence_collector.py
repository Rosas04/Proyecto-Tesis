"""
services/evidence_collector.py — Evidencias de calidad medidas en ejecución.

Durante la captura de cada interfaz se registran observaciones objetivas que
alimentan las métricas ISO/IEC 25010 (ver services/iso_framework.py):

  Seguridad      → HTTPS, certificado TLS, cabeceras (CSP, HSTS, X-Frame-Options,
                   nosniff, Referrer-Policy), redirección HTTP→HTTPS, cookies Secure,
                   contenido mixto, formularios de contraseña, credenciales en
                   Web Storage y SRI en scripts de terceros.
  Fiabilidad     → código HTTP de la interfaz, errores JavaScript no capturados,
                   errores de consola y recursos que fallan.
  Adecuación     → enlaces internos operativos e imágenes que cargan.
  Flexibilidad   → desbordamiento horizontal en 3 resoluciones y reflow a 320 px.
  Interacción    → tamaño de objetivos táctiles y tamaño de texto en móvil.
  Compatibilidad → peticiones a API exitosas, variables globales añadidas y
                   carga en Firefox y WebKit.

Las comprobaciones de red adicionales (enlaces, redirección HTTP→HTTPS y TLS)
se hacen sólo contra el mismo host ya validado por la política SSRF y sin
seguir redirecciones.
"""
from __future__ import annotations

import logging
import os
import socket
import ssl
import time
from typing import Any, Callable, Optional
from urllib.parse import urldefrag, urlparse

from core.security import is_host_allowed, validate_url

logger = logging.getLogger(__name__)

# Peticiones canceladas por el propio sistema (bloqueo de trackers/SSRF) o por
# cambio de página: no son fallos de la interfaz evaluada.
_IGNORED_FAILURES = ("ERR_BLOCKED_BY_CLIENT", "ERR_ABORTED", "NS_BINDING_ABORTED", "cancelled")

# Palabras que identifican enlaces con efectos (no se verifican ni con HEAD).
_UNSAFE_LINK_WORDS = (
    "logout", "log-out", "signout", "sign-out", "logoff", "salir", "cerrar-sesion", "cerrar_sesion",
    "delete", "remove", "destroy", "eliminar", "borrar", "unsubscribe", "desuscribir", "cancel",
    "download", "export", "descargar", "payment", "checkout", "pagar", "confirm", "action=",
)

MAX_LINKS_CHECKED = int(os.environ.get("EVIDENCE_MAX_LINKS", "15"))
LINK_CHECK_BUDGET_S = float(os.environ.get("EVIDENCE_LINK_BUDGET_S", "20"))


# ─────────────────────────────────────────────────────────────────────────────
# Registro de eventos de red y errores por interfaz
# ─────────────────────────────────────────────────────────────────────────────

class EvidenceRecorder:
    """Escucha los eventos de una página; `reset()` antes de cada navegación."""

    def __init__(self, page):
        self.page = page
        self.reset()
        page.on("request", self._on_request)
        page.on("requestfailed", self._on_failed)
        page.on("response", self._on_response)
        page.on("pageerror", self._on_pageerror)
        page.on("console", self._on_console)

    def reset(self) -> None:
        self.total = 0
        self.failed = 0
        self.api_total = 0
        self.api_failed = 0
        self.mixed = 0
        self.mixed_samples: list[str] = []
        self.failed_samples: list[str] = []
        self.js_errors: list[str] = []
        self.console_errors: list[str] = []

    @staticmethod
    def _is_api(request) -> bool:
        return request.resource_type in ("xhr", "fetch")

    def _on_request(self, request) -> None:
        try:
            self.total += 1
            if self._is_api(request):
                self.api_total += 1
            page_url = self.page.url or ""
            if page_url.startswith("https://") and request.url.startswith("http://"):
                self.mixed += 1
                if len(self.mixed_samples) < 5:
                    self.mixed_samples.append(request.url[:200])
        except Exception:
            pass

    def _register_failure(self, request, reason: str) -> None:
        self.failed += 1
        if self._is_api(request):
            self.api_failed += 1
        if len(self.failed_samples) < 5:
            self.failed_samples.append(f"{reason} · {request.url[:180]}")

    def _on_failed(self, request) -> None:
        try:
            failure = request.failure or ""
            if any(token in failure for token in _IGNORED_FAILURES):
                return
            self._register_failure(request, failure or "fallo de red")
        except Exception:
            pass

    def _on_response(self, response) -> None:
        try:
            if response.status >= 400:
                self._register_failure(response.request, f"HTTP {response.status}")
        except Exception:
            pass

    def _on_pageerror(self, error) -> None:
        if len(self.js_errors) < 50:
            self.js_errors.append(str(getattr(error, "message", error))[:300])

    def _on_console(self, message) -> None:
        try:
            if message.type == "error" and "Failed to load resource" not in message.text:
                if len(self.console_errors) < 50:
                    self.console_errors.append(message.text[:300])
        except Exception:
            pass

    def snapshot(self) -> dict[str, Any]:
        return {
            "requests": {
                "total": self.total, "failed": self.failed,
                "api_total": self.api_total, "api_failed": self.api_failed,
                "failed_samples": self.failed_samples,
            },
            "mixed_content": {"count": self.mixed, "samples": self.mixed_samples},
            "js_errors": {"count": len(self.js_errors), "samples": self.js_errors[:5]},
            "console_errors": {"count": len(self.console_errors), "samples": self.console_errors[:5]},
        }


# ─────────────────────────────────────────────────────────────────────────────
# Sondas ejecutadas en la página
# ─────────────────────────────────────────────────────────────────────────────

_PAGE_PROBE_JS = r"""
() => {
  const out = {};
  // Formularios con contraseña: deben enviarse por HTTPS y con POST
  const pwForms = [...document.querySelectorAll('form')].filter(f => f.querySelector('input[type="password" i]'));
  out.password_forms = {
    total: pwForms.length,
    // Inseguro: destino http://, o envío nativo por GET hacia un action explícito
    // (los formularios sin action los procesa JavaScript y no se envían por GET).
    insecure: pwForms.filter(f => {
      const action = f.action || location.href;
      const explicit = (f.getAttribute('action') || '').trim();
      const nativeGet = explicit && !explicit.startsWith('#') && !/^javascript:/i.test(explicit)
        && (f.getAttribute('method') || 'get').toLowerCase() !== 'post';
      return action.startsWith('http://') || nativeGet;
    }).length,
    standalone_fields: pwForms.length === 0 ? document.querySelectorAll('input[type="password" i]').length : 0,
  };
  // Imágenes que no cargan (tras el scroll de lazy-loading)
  const imgs = [...document.images].filter(i => (i.currentSrc || i.getAttribute('src') || '').trim() && i.complete);
  const broken = imgs.filter(i => i.naturalWidth === 0);
  out.images = { total: imgs.length, broken: broken.length,
                 samples: broken.slice(0, 5).map(i => (i.currentSrc || i.src || '').slice(0, 200)) };
  // Credenciales en Web Storage (OWASP: no guardar tokens de sesión en storage)
  const jwt = /^(Bearer\s+)?eyJ[\w-]{5,}\.[\w-]{5,}\./;
  const nameRe = /(token|jwt|auth|session|password|passwd|secret|credential)/i;
  const tokens = [];
  for (const store of [window.localStorage, window.sessionStorage]) {
    try {
      for (let i = 0; i < store.length; i++) {
        const k = store.key(i); const v = String(store.getItem(k) || '');
        if (jwt.test(v) || v.includes('"access_token"') || (nameRe.test(k) && v.length >= 16)) tokens.push(k.slice(0, 80));
      }
    } catch (e) {}
  }
  out.storage_credentials = { count: tokens.length, keys: tokens.slice(0, 5) };
  // Scripts de terceros y SRI
  const third = [...document.querySelectorAll('script[src]')].filter(s => {
    try { return new URL(s.src, location.href).origin !== location.origin; } catch (e) { return false; }
  });
  out.third_party_scripts = { total: third.length,
    with_sri: third.filter(s => s.integrity).length,
    samples: third.filter(s => !s.integrity).slice(0, 5).map(s => s.src.slice(0, 200)) };
  // Variables globales añadidas por la interfaz (comparadas con una ventana limpia)
  try {
    const frame = document.createElement('iframe');
    frame.style.display = 'none';
    document.documentElement.appendChild(frame);
    const base = new Set(Object.getOwnPropertyNames(frame.contentWindow));
    frame.remove();
    const added = Object.getOwnPropertyNames(window).filter(k => !base.has(k));
    out.globals = { count: added.length, samples: added.slice(0, 10) };
  } catch (e) { out.globals = null; }
  out.manifest = !!document.querySelector('link[rel="manifest"]');
  const csp = document.querySelector('meta[http-equiv="Content-Security-Policy" i]');
  out.meta_csp = csp ? (csp.getAttribute('content') || '') : '';
  // Enlaces internos (mismo origen) para verificar que respondan
  const seen = new Set();
  for (const a of document.querySelectorAll('a[href]')) {
    try {
      const u = new URL(a.getAttribute('href'), location.href);
      if (u.origin !== location.origin || !/^https?:$/.test(u.protocol)) continue;
      u.hash = '';
      seen.add(u.href);
    } catch (e) {}
    if (seen.size >= 60) break;
  }
  out.internal_links = [...seen];
  return out;
}
"""

_LAYOUT_PROBE_JS = r"""
(isMobile) => {
  const de = document.documentElement;
  const out = {
    width: window.innerWidth,
    overflow: de.scrollWidth > window.innerWidth + 1,
    scroll_width: de.scrollWidth,
    height: Math.max(de.scrollHeight, document.body ? document.body.scrollHeight : 0),
  };
  if (!isMobile) return out;
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return null;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || Number(st.opacity) === 0) return null;
    return r;
  };
  // WCAG 2.2 · 2.5.8: objetivos de al menos 24×24 px. Excepciones aplicadas:
  // enlaces dentro de una oración y objetivos pequeños con espaciado suficiente
  // (un círculo de 24 px centrado en el objetivo no toca otro objetivo).
  const items = [];
  const sel = 'a[href], button, input:not([type="hidden"]), select, textarea, [role="button"], [role="link"], [role="checkbox"], [role="tab"]';
  for (const el of [...document.querySelectorAll(sel)].slice(0, 800)) {
    const r = visible(el); if (!r) continue;
    if (el.tagName === 'A') {
      const parentText = (el.parentElement ? el.parentElement.textContent : '').trim().length;
      if (parentText > (el.textContent || '').trim().length + 20) continue;  // enlace en línea
    }
    items.push({ el, r, cx: r.left + r.width / 2, cy: r.top + r.height / 2,
                 undersized: r.width < 24 || r.height < 24 });
  }
  const distToRect = (x, y, r) => Math.hypot(Math.max(r.left - x, 0, x - r.right), Math.max(r.top - y, 0, y - r.bottom));
  let small = 0; const smallSamples = [];
  for (const a of items) {
    if (!a.undersized) continue;
    const crowded = items.some(b => b !== a && !b.el.contains(a.el) && !a.el.contains(b.el) && (
      b.undersized ? Math.hypot(a.cx - b.cx, a.cy - b.cy) < 24 : distToRect(a.cx, a.cy, b.r) < 12));
    if (crowded) {
      small += 1;
      if (smallSamples.length < 5) smallSamples.push(a.el.outerHTML.slice(0, 120));
    }
  }
  const targets = items.length;
  // Texto legible en móvil (≥ 12 px)
  let texts = 0, tiny = 0;
  for (const el of [...document.body.querySelectorAll('*')].slice(0, 3000)) {
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!hasText || !visible(el)) continue;
    texts += 1;
    if ((parseFloat(getComputedStyle(el).fontSize) || 16) < 12) tiny += 1;
  }
  return { ...out, targets, small_targets: small, small_samples: smallSamples, text_elements: texts, small_text: tiny };
}
"""


def probe_page(page) -> dict[str, Any]:
    try:
        return page.evaluate(_PAGE_PROBE_JS) or {}
    except Exception as exc:
        logger.debug("probe_page: %s", exc)
        return {}


def probe_layout(page, mobile: bool) -> Optional[dict[str, Any]]:
    try:
        return page.evaluate(_LAYOUT_PROBE_JS, mobile)
    except Exception as exc:
        logger.debug("probe_layout: %s", exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Comprobaciones de red (mismo host, sin seguir redirecciones)
# ─────────────────────────────────────────────────────────────────────────────

def _safe_link(url: str) -> bool:
    lower = url.lower()
    return validate_url(url) and not any(word in lower for word in _UNSAFE_LINK_WORDS)


def check_internal_links(page, links: list[str]) -> dict[str, Any]:
    """HEAD (o GET si HEAD no se admite) a los enlaces internos; 2xx/3xx = operativo."""
    current = urldefrag(page.url)[0]
    candidates = [u for u in links if u != current and _safe_link(u)][:MAX_LINKS_CHECKED]
    checked, broken, samples = 0, 0, []
    deadline = time.monotonic() + LINK_CHECK_BUDGET_S
    for url in candidates:
        if time.monotonic() > deadline:
            break
        try:
            resp = page.request.head(url, max_redirects=0, timeout=5_000, fail_on_status_code=False)
            status = resp.status
            if status in (403, 405, 501):
                resp = page.request.get(url, max_redirects=0, timeout=5_000, fail_on_status_code=False)
                status = resp.status
        except Exception:
            status = None   # sin respuesta (timeout / conexión)
        if status == 429:
            continue      # límite de peticiones del sitio: no concluyente
        checked += 1
        # 401/403: el recurso existe pero exige permisos (no es un enlace roto)
        if status is None or (status >= 400 and status not in (401, 403)):
            broken += 1
            if len(samples) < 5:
                samples.append(f"{status or 'sin respuesta'} · {url[:180]}")
    return {"candidates": len(candidates), "checked": checked, "broken": broken, "samples": samples}


def check_tls(hostname: str, port: int = 443, _certifi_retry: bool = False) -> dict[str, Any]:
    """Valida cadena, nombre y vigencia del certificado (almacén del sistema y, si falta la CA, certifi)."""
    if not is_host_allowed(hostname):
        return {"valid": None, "error": "host no permitido"}
    try:
        cafile = None
        if _certifi_retry:
            import certifi
            cafile = certifi.where()
        ctx = ssl.create_default_context(cafile=cafile)
        with socket.create_connection((hostname, port), timeout=6) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as tls:
                cert = tls.getpeercert() or {}
                expires = ssl.cert_time_to_seconds(cert["notAfter"]) if cert.get("notAfter") else None
                return {
                    "valid": True,
                    "protocol": tls.version(),
                    "days_to_expiry": int((expires - time.time()) / 86400) if expires else None,
                }
    except ssl.SSLCertVerificationError as exc:
        if exc.verify_code == 20 and not _certifi_retry:
            # Almacén del sistema sin la CA intermedia (frecuente en Windows):
            # se repite con el bundle de Mozilla, igual que hacen los navegadores.
            return check_tls(hostname, port, _certifi_retry=True)
        if exc.verify_code == 20:
            return {"valid": None, "error": "cadena de certificados incompleta (no concluyente)"}
        return {"valid": False, "error": (exc.verify_message or str(exc))[:200]}
    except (OSError, ssl.SSLError) as exc:
        return {"valid": None, "error": str(exc)[:200]}


def check_http_redirect(page, hostname: str) -> Optional[bool]:
    """True si http://host/ redirige a HTTPS; False si sirve contenido por HTTP."""
    url = f"http://{hostname}/"
    if not validate_url(url):
        return None
    try:
        resp = page.request.get(url, max_redirects=0, timeout=8_000, fail_on_status_code=False)
    except Exception:
        return None   # puerto 80 cerrado o sin respuesta: no concluyente
    location = (resp.headers.get("location") or "").lower()
    if 300 <= resp.status < 400:
        return location.startswith("https://")
    return False if resp.status < 400 else None


_SECURITY_HEADERS = {
    "content-security-policy": "csp",
    "strict-transport-security": "hsts",
    "x-frame-options": "x_frame_options",
    "x-content-type-options": "x_content_type_options",
    "referrer-policy": "referrer_policy",
}


def security_headers(response) -> Optional[dict[str, str]]:
    if response is None:
        return None
    try:
        headers = response.all_headers()
    except Exception:
        return None
    return {key: (headers.get(name) or "")[:300] for name, key in _SECURITY_HEADERS.items()}


def cookie_summary(context, url: str) -> dict[str, Any]:
    try:
        cookies = context.cookies([url])
    except Exception:
        return {"total": 0, "secure": 0, "insecure_samples": []}
    insecure = [c["name"] for c in cookies if not c.get("secure")]
    return {"total": len(cookies), "secure": len(cookies) - len(insecure), "insecure_samples": insecure[:5]}


def collect_network_security(page, response, host_cache: dict) -> dict[str, Any]:
    """Cabeceras, TLS, redirección HTTP→HTTPS y cookies de la interfaz actual."""
    parsed = urlparse(page.url)
    host = parsed.hostname or ""
    https = parsed.scheme == "https"
    cached = host_cache.setdefault(host, {})
    if https and "tls" not in cached:
        cached["tls"] = check_tls(host, parsed.port or 443)
    if https and "http_redirect" not in cached:
        cached["http_redirect"] = check_http_redirect(page, host)
    return {
        "navigation": {"status": response.status if response is not None else None,
                       "final_url": page.url[:500], "https": https},
        "headers": security_headers(response),
        "tls": cached.get("tls") if https else None,
        "http_redirects_to_https": cached.get("http_redirect") if https else None,
        "cookies": cookie_summary(page.context, page.url),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Compatibilidad entre navegadores (Firefox y WebKit)
# ─────────────────────────────────────────────────────────────────────────────

COMPAT_BROWSERS = [b.strip() for b in os.environ.get("COMPAT_BROWSERS", "firefox,webkit").split(",") if b.strip()]
COMPAT_MAX_INTERFACES = int(os.environ.get("COMPAT_MAX_INTERFACES", "3"))
COMPAT_BUDGET_S = float(os.environ.get("COMPAT_BUDGET_S", "150"))


def run_cross_browser(
    playwright,
    targets: list[dict[str, Any]],
    storage_state: Optional[str],
    install_guard: Callable,
    is_login_page: Callable,
) -> dict[int, dict[str, Any]]:
    """
    Abre las primeras COMPAT_MAX_INTERFACES interfaces en otros motores y
    registra si cargan, sus errores JavaScript y su diseño (desbordamiento y alto).
    Devuelve {route_index: {motor: resultado}}.
    """
    results: dict[int, dict[str, Any]] = {t["route_index"]: {} for t in targets}
    targets = targets[:COMPAT_MAX_INTERFACES]
    deadline = time.monotonic() + COMPAT_BUDGET_S

    for engine_name in COMPAT_BROWSERS:
        engine = getattr(playwright, engine_name, None)
        if engine is None:
            continue
        try:
            browser = engine.launch(headless=True)
        except Exception as exc:
            logger.warning("Navegador %s no disponible: %s", engine_name, exc)
            for t in targets:
                results[t["route_index"]][engine_name] = {"available": False}
            continue
        logger.info("Verificando compatibilidad en %s...", engine_name)
        try:
            for t in targets:
                if time.monotonic() > deadline:
                    break
                results[t["route_index"]][engine_name] = _load_in_engine(
                    browser, t, storage_state, install_guard, is_login_page)
        finally:
            try:
                browser.close()
            except Exception:
                pass
    return results


def _load_in_engine(browser, target, storage_state, install_guard, is_login_page) -> dict[str, Any]:
    args: dict[str, Any] = {"viewport": {"width": 1366, "height": 768}, "ignore_https_errors": True}
    if target.get("is_internal") and storage_state and os.path.exists(storage_state):
        args["storage_state"] = storage_state
    context = browser.new_context(**args)
    errors: list[str] = []
    try:
        install_guard(context)
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(str(getattr(e, "message", e))[:200]))
        response = page.goto(target["url"], wait_until="domcontentloaded", timeout=20_000)
        try:
            page.wait_for_load_state("networkidle", timeout=3_000)
        except Exception:
            pass
        page.wait_for_timeout(500)
        if target.get("is_internal") and is_login_page(page):
            return {"available": True, "session_lost": True}
        desktop = probe_layout(page, False) or {}
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(400)
        mobile = probe_layout(page, False) or {}
        status = response.status if response is not None else None
        body_text = page.evaluate("() => (document.body ? document.body.innerText.trim().length : 0)")
        return {
            "available": True,
            "status": status,
            "loaded": (status is None or status < 400) and body_text > 0,
            "js_errors": len(errors),
            "js_error_samples": errors[:3],
            "overflow_desktop": desktop.get("overflow"),
            "overflow_mobile": mobile.get("overflow"),
            "height": desktop.get("height"),
        }
    except Exception as exc:
        return {"available": True, "loaded": False, "error": str(exc).splitlines()[0][:200]}
    finally:
        try:
            context.close()
        except Exception:
            pass
