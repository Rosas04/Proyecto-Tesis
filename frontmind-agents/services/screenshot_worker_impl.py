from __future__ import annotations

import logging
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from services.auth_service import (
    normalize_auth_config,
    perform_form_login,
    save_storage_state,
)
from services.route_discovery_service import (
    discover_routes,
    discover_routes_authenticated,
    extract_internal_links,
    is_auth_page_url,
)
from services.spa_helpers import wait_for_spa
from core.security import is_host_allowed, validate_url

logger = logging.getLogger(__name__)

CAPTURES_DIR = Path("captures")
DEFAULT_API_BASE_URL = "http://127.0.0.1:8001"

# Límites del cache de CSS capturado (evita respuestas gigantes al frontend)
_MAX_CSS_SHEET_CHARS = 2_000_000
_MAX_CSS_CACHE_CHARS = 10_000_000

# Única definición de VIEWPORTS — reutilizada en todas las funciones del módulo
VIEWPORTS: list[dict[str, Any]] = [
    {"device": "desktop", "width": 1366, "height": 768},
    {"device": "tablet",  "width": 768,  "height": 1024},
    {"device": "mobile",  "width": 390,  "height": 844},
]

# Rutas de trackers que bloquear para evitar cuelgues de networkidle
_TRACKER_PATTERNS = [
    "**/*google-analytics*",
    "**/*googletagmanager*",
    "**/*hotjar*",
    "**/*facebook.net*",
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"https?://", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:80] or "interface"


def collect_dom_metrics(page) -> dict[str, int]:
    return page.evaluate(
        """
        () => ({
            total_nodes: document.querySelectorAll('*').length,
            buttons: document.querySelectorAll('button, [role="button"]').length,
            links: document.querySelectorAll('a[href]').length,
            inputs: document.querySelectorAll('input, textarea, select').length,
            images: document.querySelectorAll('img').length,
            forms: document.querySelectorAll('form').length,
            tables: document.querySelectorAll('table').length,
            dialogs: document.querySelectorAll(
                'dialog, [role="dialog"], [aria-modal="true"]'
            ).length,
            headings: document.querySelectorAll(
                'h1, h2, h3, h4, h5, h6'
            ).length,
            semantic_elements: document.querySelectorAll(
                'main, nav, header, footer, section, article, aside'
            ).length
        })
        """
    )


_PERFORMANCE_JS = """
() => new Promise((resolve) => {
    const nav = performance.getEntriesByType('navigation')[0];
    const resources = performance.getEntriesByType('resource');
    let lcp = null;
    let cls = 0;
    try {
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            if (entries.length) lcp = entries[entries.length - 1].startTime;
        }).observe({ type: 'largest-contentful-paint', buffered: true });
    } catch (e) {}
    try {
        new PerformanceObserver((list) => {
            for (const e of list.getEntries()) if (!e.hadRecentInput) cls += e.value;
        }).observe({ type: 'layout-shift', buffered: true });
    } catch (e) {}
    setTimeout(() => resolve({
        ttfb_ms: nav ? Math.max(0, nav.responseStart - nav.requestStart) : null,
        dom_content_loaded_ms: nav && nav.domContentLoadedEventEnd ? nav.domContentLoadedEventEnd : null,
        load_ms: nav && nav.loadEventEnd ? nav.loadEventEnd : null,
        lcp_ms: lcp,
        cls: Math.round(cls * 1000) / 1000,
        requests: resources.length + 1,
        transfer_bytes: (nav ? nav.transferSize || 0 : 0)
            + resources.reduce((acc, r) => acc + (r.transferSize || 0), 0),
        js_heap_mb: performance.memory
            ? Math.round(performance.memory.usedJSHeapSize / 1048576 * 10) / 10 : null,
    }), 300);
})
"""


def collect_performance_metrics(page) -> dict[str, Any]:
    """
    Métricas de ejecución de la navegación actual (ISO/IEC 25010 · eficiencia
    de desempeño): TTFB, LCP, CLS, peticiones, bytes transferidos y memoria JS.
    Se miden una sola vez desde el servidor de evaluación.
    """
    try:
        metrics = page.evaluate(_PERFORMANCE_JS)
        return {k: v for k, v in (metrics or {}).items() if v is not None}
    except Exception as exc:
        logger.debug("No se pudieron obtener métricas de desempeño: %s", exc)
        return {}


def extract_cssom_styles(page) -> list[str]:
    try:
        extracted = page.evaluate("""() => {
            const styles = [];
            for (const sheet of document.styleSheets) {
                try {
                    const rules = sheet.cssRules || sheet.rules;
                    if (rules) {
                        let content = "";
                        for (const rule of rules) {
                            content += rule.cssText + "\\n";
                        }
                        if (content.trim()) {
                            styles.push(content);
                        }
                    }
                } catch (e) {}
            }
            return styles;
        }""")
        if isinstance(extracted, list):
            return extracted
    except Exception:
        pass
    return []


def _is_on_login_page(page) -> bool:
    """
    Verifica si la página actual parece ser un formulario de login.
    Usado para detectar si el inicio de sesión falló o la sesión se perdió.
    """
    current_url = page.url.lower()

    # Si estamos explícitamente en una página de configuración o perfil, 
    # es muy probable que no sea login aunque haya un campo password.
    if any(keyword in current_url for keyword in ["profile", "settings", "account", "config", "perfil", "cuenta"]):
        return False

    # Verificar por URL explícita de autenticación
    if is_auth_page_url(page.url):
        return True

    # Verificar por contenido: ¿tiene campo de contraseña visible?
    # Para evitar falsos positivos en páginas de "Cambiar contraseña", 
    # comprobaremos que también haya un campo de texto/email genérico 
    # que parezca ser de nombre de usuario/correo.
    try:
        password_fields = page.locator("input[type='password']")
        if password_fields.count() > 0 and password_fields.first.is_visible():
            # Buscar si existe un posible campo de usuario visible
            user_fields = page.locator("input[type='email'], input[type='text'], input:not([type])")
            if user_fields.count() > 0:
                for i in range(user_fields.count()):
                    if user_fields.nth(i).is_visible():
                        return True
            # Si hay password pero NO hay campo de usuario/email visible, 
            # probablemente sea "Cambiar contraseña" (donde a veces se pide current_password)
    except Exception:
        pass

    return False


def _run_token() -> str:
    """
    Identificador único por ejecución: timestamp + 128 bits aleatorios.
    Evita colisiones entre capturas concurrentes y hace que las URLs públicas
    de /captures no sean adivinables (pueden contener vistas autenticadas).
    """
    return f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(16)}"


def _install_ssrf_guard(target) -> None:
    """
    Bloquea cualquier request (navegación, redirección o subrecurso) hacia
    hosts internos/privados o esquemas no http(s). `target` puede ser un
    BrowserContext o una Page.
    """
    def guard(route):
        try:
            parsed = urlparse(route.request.url)
            scheme = parsed.scheme.lower()
            if scheme in ("http", "https", "ws", "wss"):
                if not is_host_allowed(parsed.hostname or ""):
                    logger.warning("Request bloqueado por política SSRF: %s", parsed.hostname)
                    route.abort("blockedbyclient")
                    return
            elif scheme not in ("data", "blob", "about"):
                route.abort("blockedbyclient")
                return
            route.fallback()
        except Exception:
            try:
                route.abort()
            except Exception:
                pass

    target.route("**/*", guard)


def _block_trackers(page) -> None:
    """Bloquea trackers conocidos para evitar cuelgues de networkidle."""
    def safe_abort(route):
        try:
            route.abort()
        except Exception:
            pass
            
    for pattern in _TRACKER_PATTERNS:
        page.route(pattern, safe_abort)


def _build_route_result(
    route_index: int,
    route_url: str,
    display_name: str,
) -> dict[str, Any]:
    """Construye el dict base de resultado para una interfaz."""
    parsed_route = urlparse(route_url)
    return {
        "route_index": route_index,
        "interface_id": slugify(display_name),
        "name": display_name,
        "route": parsed_route.path,
        "url": route_url,
        "absolute_url": route_url,
        "file_name": f"interface_{route_index}.html",
        "title": display_name,
        "status": "pending",
        "capture_time_seconds": 0.0,
        "html_content": "",
        "html_length": 0,
        "cssom_styles": [],
        "performance_metrics": {},
        "dom_metrics": {},
        "captures": [],
        "errors": [],
    }


_GENERIC_SEGMENTS = {"page", "p", "index", "index.html", "index.php", "default.aspx", "home"}


def _humanize(segment: str) -> str:
    segment = re.sub(r"\.(html?|php|aspx?)$", "", segment, flags=re.IGNORECASE)
    return segment.replace("-", " ").replace("_", " ").strip().title()


def _name_from_path(path: str) -> str:
    """
    Nombre legible a partir de un path. Ignora segmentos genéricos o numéricos
    al elegir el nombre y los agrega como sufijo de página:
      /tag/books/page/2/  -> "Books (pág. 2)"
      /author/Jane-Austen -> "Jane Austen"
      /cursos/123         -> "Cursos 123"
    """
    segments = [seg for seg in path.split("?")[0].strip("/").split("/") if seg]
    if not segments:
        return ""

    page_number = None
    if len(segments) >= 2 and segments[-1].isdigit() and segments[-2].lower() in ("page", "p"):
        page_number = segments[-1]
        segments = segments[:-2]

    meaningful = [seg for seg in segments if seg.lower() not in _GENERIC_SEGMENTS]
    if not meaningful:
        name = "Home"
    elif meaningful[-1].isdigit() and len(meaningful) >= 2:
        name = f"{_humanize(meaningful[-2])} {meaningful[-1]}"
    else:
        name = _humanize(meaningful[-1])

    if page_number and page_number != "1":
        name = f"{name} (pág. {page_number})"
    return name


def _get_display_name(route_url: str) -> str:
    """Extrae un nombre legible para la interfaz a partir de su URL."""
    from urllib.parse import parse_qs, urlparse
    parsed = urlparse(route_url)

    # 1. Fragment de SPA con HashRouter (#/ruta o #!/ruta)
    if parsed.fragment and (parsed.fragment.startswith("/") or parsed.fragment.startswith("!/")):
        name = _name_from_path(parsed.fragment.lstrip("!"))
        if name:
            return name

    # 2. Path normal
    name = _name_from_path(parsed.path)
    if name and name != "Home":
        return name

    # 3. Sin path: buscar en query parameters
    if parsed.query:
        query_params = parse_qs(parsed.query)
        for key in ["page", "view", "section", "tab", "action"]:
            if key in query_params and query_params[key]:
                return _humanize(str(query_params[key][0]))

        first_val = next(iter(query_params.values()), [""])[0]
        if first_val and len(str(first_val)) < 20:
            return f"Home ({first_val})"

    return "Home"


def _route_key(route_url: str) -> str:
    """
    Clave para detectar rutas equivalentes: ignora el esquema (http/https),
    "www.", la barra final, "index.html" y una paginación "/page/1".
    """
    parsed = urlparse(route_url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    path = re.sub(r"/(index\.(html?|php))$", "", parsed.path, flags=re.IGNORECASE)
    path = re.sub(r"/page/1/?$", "", path.rstrip("/"))
    key = f"{host}{path.rstrip('/')}"
    if parsed.query:
        key += f"?{parsed.query}"
    if parsed.fragment.startswith(("/", "!/")):
        key += f"#{parsed.fragment}"
    return key


def _capture_single_page(
    page,
    route_url: str,
    route_index: int,
    timestamp: str,
    api_base_url: str,
    global_css_cache: dict,
) -> dict[str, Any]:
    """
    Captura HTML, métricas DOM, CSSOM y screenshots de una sola página.
    Asume que la página ya fue navegada y la SPA terminó de cargar.
    """
    display_name = _get_display_name(route_url)
    route_result = _build_route_result(route_index, route_url, display_name)

    try:
        # Métricas de desempeño ANTES del scroll (el scroll alteraría LCP/CLS)
        route_result["performance_metrics"] = collect_performance_metrics(page)

        # Scroll para activar lazy-loading
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(300)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(300)
        except Exception:
            pass

        route_result["html_content"] = page.content()
        route_result["cssom_styles"] = extract_cssom_styles(page)
        route_result["dom_metrics"] = collect_dom_metrics(page)
        route_result["title"] = page.title()

        # Screenshots en cada viewport
        for viewport in VIEWPORTS:
            try:
                page.set_viewport_size(
                    {"width": viewport["width"], "height": viewport["height"]}
                )
                page.wait_for_timeout(500)

                file_name = (
                    f"{timestamp}_"
                    f"{route_index:02d}_"
                    f"{slugify(route_url)}_"
                    f"{viewport['device']}.png"
                )
                file_path = CAPTURES_DIR / file_name

                page.screenshot(path=str(file_path), full_page=True)

                route_result["captures"].append({
                    "device": viewport["device"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "file_name": file_name,
                    "file_path": str(file_path),
                    "public_url": f"{api_base_url.rstrip('/')}/captures/{file_name}",
                    "success": True,
                })
            except Exception as exc:
                route_result["errors"].append({
                    "device": viewport["device"],
                    "message": str(exc),
                })

    except Exception as exc:
        route_result["errors"].append({
            "device": "general",
            "message": str(exc),
        })

    successful = sum(1 for c in route_result["captures"] if c.get("success"))
    route_result["successful_captures"] = successful
    route_result["status"] = "completed" if successful > 0 else "error"

    return route_result


# ─────────────────────────────────────────────────────────────────────────────
# Función principal de captura
# ─────────────────────────────────────────────────────────────────────────────

def take_screenshots(
    url: str,
    auth: dict[str, Any] | None = None,
    max_pages: int = 10,
) -> dict[str, Any]:
    """
    Captura interfaces de una URL, con soporte para autenticación.

    Flujo autenticado:
      1. Navegar a la URL → página de login
      2. Extraer enlaces públicos (register, forgot-password, etc.)
      3. Iniciar sesión con las credenciales
      4. Verificar que el login fue exitoso
      5. Guardar storage_state (cookies + localStorage)
      6. Descubrir rutas internas desde la página post-login
      7. Capturar páginas públicas con contexto limpio
      8. Capturar páginas internas con contexto autenticado (storage_state)
      9. Limpiar storage_state al final

    Flujo público (sin auth):
      1. Navegar a la URL
      2. Descubrir rutas con BFS
      3. Capturar cada ruta
    """
    api_base_url = os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL)
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    auth_config = normalize_auth_config(auth)
    is_authenticated = auth_config["mode"] != "none"

    timestamp = _run_token()

    results: list[dict[str, Any]] = []
    global_css_cache: dict[str, str] = {}
    generated_state_path: str | None = None

    def handle_response(response):
        try:
            if response.request.resource_type == "stylesheet":
                url_str = response.url
                if url_str not in global_css_cache:
                    used = sum(len(v) for v in global_css_cache.values())
                    if used >= _MAX_CSS_CACHE_CHARS:
                        return
                    text = response.text()
                    if len(text) <= _MAX_CSS_SHEET_CHARS:
                        global_css_cache[url_str] = text
        except Exception:
            pass

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:

                base_context_args: dict[str, Any] = {
                    "ignore_https_errors": True,
                    "user_agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                }

                # El storage_state sólo se genera internamente tras el login; nunca se
                # acepta una ruta enviada por el cliente.
                storage_state_for_capture: str | None = None
                initial_context_args = {**base_context_args}

                # ════════════════════════════════════════════════════════════════════
                # FASE 1: DESCUBRIMIENTO DE RUTAS
                # ════════════════════════════════════════════════════════════════════

                pre_login_routes: list[str] = []   # Páginas públicas (login, register, etc.)
                post_login_routes: list[str] = []  # Páginas internas (dashboard, etc.)
                login_succeeded = False

                if is_authenticated:
                    logger.info("=== FLUJO AUTENTICADO para %s ===", url)

                    # ── Paso 1: Abrir la página de login y extraer enlaces públicos ──
                    login_url = auth_config.get("login_url") or url

                    discovery_context = browser.new_context(**initial_context_args)
                    _install_ssrf_guard(discovery_context)
                    discovery_page = discovery_context.new_page()
                    _block_trackers(discovery_page)
                    discovery_page.on("dialog", lambda dialog: dialog.dismiss())

                    try:
                        discovery_page.goto(
                            login_url,
                            wait_until="domcontentloaded",
                            timeout=20_000,
                        )
                        wait_for_spa(discovery_page)

                        # Extraer enlaces públicos de la página de login
                        public_links = extract_internal_links(discovery_page, login_url)
                        pre_login_routes.append(discovery_page.url)  # la propia página de login

                        for link in public_links:
                            if link not in pre_login_routes and len(pre_login_routes) < 5:
                                pre_login_routes.append(link)

                        logger.info(
                            "Rutas públicas descubiertas ANTES del login: %s",
                            pre_login_routes,
                        )

                    except Exception as exc:
                        logger.warning("Error extrayendo rutas públicas: %s", exc)
                        pre_login_routes = [login_url]

                    # ── Paso 2: Iniciar sesión ──
                    try:
                        logger.info("Ejecutando login en %s...", login_url)
                        perform_form_login(
                            discovery_page,
                            auth_config,
                            url=url,
                        )

                        # Verificar que el login fue exitoso
                        current_url_after_login = discovery_page.url
                        logger.info(
                            "URL después del login: %s", current_url_after_login
                        )

                        if _is_on_login_page(discovery_page):
                            logger.warning(
                                "⚠️ El login pudo haber fallado — sigo en la página de auth: %s",
                                current_url_after_login,
                            )
                        else:
                            login_succeeded = True
                            logger.info("✅ Login exitoso — ahora en: %s", current_url_after_login)

                        # Guardar storage_state SIEMPRE (incluso si el login pudo fallar,
                        # porque puede tener cookies válidas)
                        generated_state_path = f"playwright/.auth/session_{timestamp}.json"
                        save_storage_state(discovery_context, generated_state_path)
                        storage_state_for_capture = generated_state_path
                        logger.info("Storage state guardado en: %s", generated_state_path)

                    except Exception as exc:
                        logger.exception("Error durante el login: %s", exc)

                    # ── Paso 3: Descubrir rutas internas post-login ──
                    if login_succeeded:
                        try:
                            # Si la URL objetivo es distinta, y actualmente seguimos en login o la url tiene un path específico
                            # Mejor: Si current_url no es auth, ya estamos dentro, quedarse ahí.
                            if is_auth_page_url(discovery_page.url) and url != login_url and not is_auth_page_url(url):
                                discovery_page.goto(
                                    url,
                                    wait_until="domcontentloaded",
                                    timeout=15_000,
                                )

                            wait_for_spa(discovery_page)

                            # Usar descubrimiento seguro para apps autenticadas:
                            # extrae enlaces SIN navegar (no rompe la sesión SPA)
                            post_login_routes = discover_routes_authenticated(
                                discovery_page,
                                start_url=discovery_page.url,
                                max_pages=max_pages,
                            )

                            logger.info(
                                "Rutas internas descubiertas DESPUÉS del login: %s",
                                post_login_routes,
                            )
                        except Exception as exc:
                            logger.exception(
                                "Error descubriendo rutas internas: %s", exc
                            )

                    # discovery_context.close()  # NO LO CERRAMOS PARA REUTILIZAR EL SESSIONSTORAGE

                else:
                    # ── Flujo público (sin autenticación) ──
                    logger.info("=== FLUJO PÚBLICO para %s ===", url)

                    discovery_context = browser.new_context(**initial_context_args)
                    _install_ssrf_guard(discovery_context)
                    discovery_page = discovery_context.new_page()
                    _block_trackers(discovery_page)
                    discovery_page.on("dialog", lambda dialog: dialog.dismiss())

                    try:
                        discovery_page.goto(
                            url,
                            wait_until="domcontentloaded",
                            timeout=15_000,
                        )
                        wait_for_spa(discovery_page)

                        # Bloquear assets pesados para descubrimiento rápido (no hay sesión que romper)
                        def safe_abort_assets(route):
                            try:
                                route.abort()
                            except Exception:
                                pass
                
                        discovery_page.route(
                            "**/*.{png,jpg,jpeg,gif,svg,mp4,webm,woff,woff2,ico}",
                            safe_abort_assets,
                        )

                        pre_login_routes = discover_routes(
                            discovery_page,
                            start_url=discovery_page.url,
                            max_pages=max_pages,
                        )
                    except Exception as exc:
                        logger.exception("Error descubriendo rutas públicas: %s", exc)
                        pre_login_routes = [url]

                    discovery_context.close()

                # ════════════════════════════════════════════════════════════════════
                # FASE 2: COMBINAR RUTAS (eliminar duplicados)
                # ════════════════════════════════════════════════════════════════════

                all_routes: list[str] = []
                internal_route_set: set[str] = set()

                seen_keys: set[str] = set()

                # Primero las rutas internas (son las más importantes)
                for route in post_login_routes:
                    key = _route_key(route)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_routes.append(route)
                        internal_route_set.add(route.rstrip("/"))

                # Luego las rutas públicas (si no se solapan con las internas).
                # Se descartan equivalentes: http/https, "/page/1", "index.html".
                for route in pre_login_routes:
                    key = _route_key(route)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_routes.append(route)

                if not all_routes:
                    all_routes = [url]

                # SSRF: descartar rutas descubiertas que apunten a hosts internos
                safe_routes = [r for r in all_routes if validate_url(r)]
                if len(safe_routes) != len(all_routes):
                    logger.warning(
                        "Se descartaron %d rutas por política de seguridad.",
                        len(all_routes) - len(safe_routes),
                    )
                all_routes = safe_routes

                logger.info(
                    "Total de rutas a capturar: %d — Internas: %d, Públicas: %d",
                    len(all_routes),
                    len(internal_route_set),
                    len(all_routes) - len(internal_route_set),
                )

                # ════════════════════════════════════════════════════════════════════
                # FASE 3: CAPTURA DE CADA RUTA
                # ════════════════════════════════════════════════════════════════════

                # Para rutas internas: usar contexto con storage_state
                # Para rutas públicas: usar contexto limpio
                # Usamos un contexto por tipo para eficiencia

                auth_capture_context = None
                auth_capture_page = None
                public_capture_context = None
                public_capture_page = None

                try:
                    for route_index, route_url in enumerate(all_routes, start=1):
                        is_internal = route_url.rstrip("/") in internal_route_set

                        logger.info(
                            "Capturando [%d/%d] %s (%s)...",
                            route_index, len(all_routes), route_url,
                            "INTERNA" if is_internal else "PÚBLICA",
                        )

                        if is_internal:
                            # ── Captura con sesión autenticada ──
                            if auth_capture_context is None:
                                auth_capture_context = discovery_context
                                auth_capture_page = discovery_page
                                _block_trackers(auth_capture_page)
                                auth_capture_page.on("response", handle_response)
                                auth_capture_page.on("dialog", lambda d: d.dismiss())

                            page = auth_capture_page
                        else:
                            # ── Captura sin autenticación ──
                            if public_capture_context is None:
                                public_capture_context = browser.new_context(**base_context_args)
                                _install_ssrf_guard(public_capture_context)
                                public_capture_page = public_capture_context.new_page()
                                _block_trackers(public_capture_page)
                                public_capture_page.on("response", handle_response)
                                public_capture_page.on("dialog", lambda d: d.dismiss())

                            page = public_capture_page

                        try:
                            page.goto(
                                route_url,
                                wait_until="domcontentloaded",
                                timeout=20_000,
                            )
                            wait_for_spa(page)

                            # Verificar que la sesión no se perdió para rutas internas
                            if is_internal and _is_on_login_page(page):
                                actual_url = page.url
                                logger.warning(
                                    "⚠️ Sesión perdida al navegar a %s (redirigido a %s). "
                                    "Recreando contexto...",
                                    route_url, actual_url,
                                )
                                # Recrear el contexto con storage_state fresco
                                try:
                                    auth_capture_context.close()
                                except Exception:
                                    pass

                                auth_context_args = {
                                    **base_context_args,
                                    "storage_state": storage_state_for_capture,
                                }
                                auth_capture_context = browser.new_context(**auth_context_args)
                                _install_ssrf_guard(auth_capture_context)
                                auth_capture_page = auth_capture_context.new_page()
                                _block_trackers(auth_capture_page)
                                auth_capture_page.on("response", handle_response)
                                auth_capture_page.on("dialog", lambda d: d.dismiss())
                                page = auth_capture_page

                                page.goto(
                                    route_url,
                                    wait_until="domcontentloaded",
                                    timeout=20_000,
                                )
                                wait_for_spa(page)

                                # Si sigue en login, marcar como error y continuar
                                if _is_on_login_page(page):
                                    logger.error(
                                        "❌ No se pudo restaurar la sesión para %s. Saltando.",
                                        route_url,
                                    )
                                    display_name = _get_display_name(route_url)
                                    error_result = _build_route_result(route_index, route_url, display_name)
                                    error_result["status"] = "error"
                                    error_result["errors"].append({
                                        "device": "general",
                                        "message": "Sesión perdida — la página redirige al login.",
                                    })
                                    results.append(error_result)
                                    continue

                            # Capturar la página
                            result = _capture_single_page(
                                page=page,
                                route_url=route_url,
                                route_index=route_index,
                                timestamp=timestamp,
                                api_base_url=api_base_url,
                                global_css_cache=global_css_cache,
                            )
                            results.append(result)

                        except Exception as exc:
                            logger.exception("Error capturando %s: %s", route_url, exc)
                            display_name = _get_display_name(route_url)
                            error_result = _build_route_result(route_index, route_url, display_name)
                            error_result["status"] = "error"
                            error_result["errors"].append({
                                "device": "general",
                                "message": str(exc),
                            })
                            results.append(error_result)

                finally:
                    # Cerrar contextos de captura
                    if auth_capture_context:
                        try:
                            auth_capture_context.close()
                        except Exception:
                            pass
                    if public_capture_context:
                        try:
                            public_capture_context.close()
                        except Exception:
                            pass

            finally:
                try:
                    browser.close()
                except Exception:
                    pass
    finally:
        # ════════════════════════════════════════════════════════════════
        # LIMPIEZA: eliminar storage_state SIEMPRE (también si hubo error)
        # ════════════════════════════════════════════════════════════════
        if generated_state_path and Path(generated_state_path).exists():
            try:
                os.remove(generated_state_path)
                logger.debug("Sesión temporal eliminada.")
            except OSError as exc:
                logger.warning("No se pudo eliminar la sesión temporal: %s", exc)

    # ════════════════════════════════════════════════════════════════════
    # RESULTADO FINAL
    # ════════════════════════════════════════════════════════════════════

    main_page_data = results[0] if results else None
    html_content = main_page_data["html_content"] if main_page_data else ""
    captures = main_page_data["captures"] if main_page_data else []
    cssom_styles = main_page_data["cssom_styles"] if main_page_data else []
    performance_metrics = main_page_data.get("performance_metrics", {}) if main_page_data else {}

    total_routes = len(post_login_routes) + len(pre_login_routes)

    return {
        "source_type": "authenticated_url" if is_authenticated else "public_url",
        "status": "completed",
        "start_url": url,
        "url": url,
        "authentication_mode": auth_config["mode"],
        "login_succeeded": login_succeeded,
        "authenticated_state_created": bool(storage_state_for_capture),
        "routes_discovered": total_routes,
        "interfaces": results,
        "total_interfaces": len(results),
        "total_captures": sum(len(iface["captures"]) for iface in results),
        "captured_at": timestamp,
        "html_content": html_content,
        "captures": captures,
        "css_cache": global_css_cache,
        "cssom_styles": cssom_styles,
        "performance_metrics": performance_metrics,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Funciones auxiliares para ZIP (sin cambios)
# ─────────────────────────────────────────────────────────────────────────────

def take_screenshots_from_html(html_content: str, label: str = "zip"):
    """Generate viewport screenshots from raw HTML using Playwright set_content()."""
    api_base_url = os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL)
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = _run_token()
    captures = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        for item in VIEWPORTS:
            page = browser.new_page(
                viewport={"width": item["width"], "height": item["height"]},
            )
            _install_ssrf_guard(page)

            try:
                page.set_content(html_content, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)

                file_name = f"{label}_{item['device']}_{timestamp}.png"
                file_path = output_dir / file_name

                page.screenshot(path=str(file_path), full_page=True)

                captures.append({
                    "device": item["device"],
                    "width": item["width"],
                    "height": item["height"],
                    "file_name": file_name,
                    "file_path": str(file_path),
                    "public_url": f"{api_base_url.rstrip('/')}/captures/{file_name}",
                })

            except Exception as e:
                captures.append({
                    "device": item["device"],
                    "width": item["width"],
                    "height": item["height"],
                    "error": str(e),
                })
            finally:
                page.close()

        browser.close()

    return {
        "captures": captures,
        "total_captures": len(captures),
        "captured_at": timestamp,
    }


def take_screenshots_for_multiple_htmls(htmls: dict, label_prefix: str = "zip"):
    """Generate viewport screenshots from multiple HTML contents using a single Playwright session."""
    api_base_url = os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL)
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = _run_token()
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        for key, html_content in htmls.items():
            if not html_content or not html_content.strip():
                results[key] = []
                continue

            captures = []
            safe_key = re.sub(r'[^a-zA-Z0-9_-]', '_', key)[:30]

            for item in VIEWPORTS:

                page = browser.new_page(
                    viewport={"width": item["width"], "height": item["height"]},
                )
                _install_ssrf_guard(page)

                try:
                    page.set_content(html_content, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1500)

                    file_name = f"{label_prefix}_{safe_key}_{item['device']}_{timestamp}.png"
                    file_path = output_dir / file_name

                    page.screenshot(path=str(file_path), full_page=True)

                    captures.append({
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "file_name": file_name,
                        "file_path": str(file_path),
                        "public_url": f"{api_base_url.rstrip('/')}/captures/{file_name}",
                    })

                except Exception as e:
                    captures.append({
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "error": str(e),
                    })
                finally:
                    page.close()

            results[key] = captures

        browser.close()

    return results
