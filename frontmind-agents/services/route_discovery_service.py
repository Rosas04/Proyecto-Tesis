from __future__ import annotations

import logging
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

from playwright.sync_api import Page
from services.spa_helpers import wait_for_spa

logger = logging.getLogger(__name__)

EXCLUDED_PATH_WORDS = {
    "logout",
    "signout",
    "logoff",
    "cerrar-sesion",
    "delete",
    "remove",
    "destroy",
    "eliminar",
    "download",
    "export",
    "payment",
    "pay",
    "checkout",
    "confirm",
    "admin/delete",
}

# Rutas de autenticación que no deben capturarse como interfaces internas
AUTH_PATH_WORDS = {
    "login",
    "signin",
    "sign-in",
    "register",
    "signup",
    "sign-up",
    "forgot-password",
    "forgot_password",
    "reset-password",
    "reset_password",
    "auth",
    "sso",
    "oauth",
    "callback",
    "verify-email",
    "verify_email",
    "confirm-email",
    "confirm_email",
}


def normalize_url(base_url: str, candidate: str) -> str | None:
    if not candidate:
        return None

    absolute = urljoin(base_url, candidate)
    
    # Preservar fragments si parecen ser rutas de un SPA (HashRouter)
    if "#/" in absolute or "#!" in absolute:
        # SPA route, keep it
        pass
    else:
        # Standard anchor link, safe to defrag
        absolute, _fragment = urldefrag(absolute)

    parsed = urlparse(absolute)

    if parsed.scheme not in {"http", "https"}:
        return None

    return absolute


def is_safe_internal_url(
    candidate: str,
    origin: str,
) -> bool:
    parsed_candidate = urlparse(candidate)
    parsed_origin = urlparse(origin)

    def get_base(netloc: str) -> str:
        parts = netloc.split('.')
        if len(parts) >= 2:
            if parts[-2] in ["edu", "com", "gov", "org", "net", "mil", "gob"] and len(parts) >= 3:
                return ".".join(parts[-3:])
            return ".".join(parts[-2:])
        return netloc

    base_candidate = get_base(parsed_candidate.netloc)
    base_origin = get_base(parsed_origin.netloc)

    if base_candidate != base_origin:
        return False

    lower_path = parsed_candidate.path.lower()

    if any(word in lower_path for word in EXCLUDED_PATH_WORDS):
        return False

    return True


def is_auth_page_url(url: str) -> bool:
    """Detecta si una URL corresponde a una página de autenticación (login, register, etc.)."""
    lower_path = urlparse(url).path.lower().strip("/")
    # Verificar segmentos individuales del path
    segments = lower_path.split("/")
    for segment in segments:
        if segment in AUTH_PATH_WORDS:
            return True
    return False


def extract_internal_links(
    page: Page,
    origin: str,
) -> list[str]:
    """
    Extrae enlaces internos del DOM actual.
    Versión mejorada con selectores amplios para SPAs.
    """
    raw_links = page.evaluate(
        """
        () => {
            const getLinks = (root) => {
                let urls = [];
                
                // 1. Standard anchors — en todo el documento
                root.querySelectorAll('a[href], [role="link"][href]').forEach(el => {
                    urls.push(el.getAttribute('href'));
                });
                
                // 2. Data attributes de navegación
                root.querySelectorAll('[data-href], [data-url], [data-link], [data-route], [data-path]').forEach(el => {
                    urls.push(
                        el.getAttribute('data-href') || 
                        el.getAttribute('data-url') || 
                        el.getAttribute('data-link') ||
                        el.getAttribute('data-route') ||
                        el.getAttribute('data-path')
                    );
                });
                
                // 3. Sidebar / Nav / Menu — buscar enlaces en contenedores de navegación
                const navContainers = root.querySelectorAll(
                    'nav, [role="navigation"], ' +
                    '[class*="sidebar"], [class*="side-bar"], [class*="sidenav"], ' +
                    '[class*="menu"], [class*="drawer"], ' +
                    '[class*="navbar"], [class*="nav-bar"], [class*="topbar"], ' +
                    '[class*="header"] nav, header nav, ' +
                    'aside, [role="complementary"]'
                );
                navContainers.forEach(container => {
                    container.querySelectorAll('a[href]').forEach(el => {
                        urls.push(el.getAttribute('href'));
                    });
                });
                
                // 4. React Router Links (NavLink, Link) — suelen ser <a> con href
                //    pero también pueden ser elementos con to="" attribute
                root.querySelectorAll('[to], [data-to]').forEach(el => {
                    urls.push(el.getAttribute('to') || el.getAttribute('data-to'));
                });
                
                // 5. Check shadow roots
                root.querySelectorAll('*').forEach(el => {
                    if (el.shadowRoot) urls = urls.concat(getLinks(el.shadowRoot));
                });
                
                return urls;
            };
            return getLinks(document);
        }
        """
    )

    links: list[str] = []

    for raw_link in raw_links:
        normalized = normalize_url(page.url, raw_link)

        if not normalized:
            continue

        if not is_safe_internal_url(normalized, origin):
            continue

        if normalized not in links:
            links.append(normalized)

    return links


def extract_routes_via_clicks(page: Page, origin: str) -> list[str]:
    """
    Descubre rutas haciendo click en elementos de navegación.
    SOLO para flujo público — NO usar en flujo autenticado.
    """
    discovered_urls = []
    try:
        # Find potential navigation elements that DON'T have hrefs (since we already got those)
        locators = page.locator("button:not([disabled]), [role='button']:not([disabled]), [role='link']:not([href]), [class*='nav']:not(nav), [class*='menu-item'], [class*='tab'], li:not(:has(a))").all()
        # Limit to first 20 to avoid excessive clicking and massive time delays, prioritize visible ones
        locators = [loc for loc in locators if loc.is_visible()][:20]
        
        for loc in locators:
            try:
                text = (loc.inner_text() or "").lower()
                class_name = (loc.get_attribute("class") or "").lower()
                
                # Exclude destructive actions
                excluded_terms = [
                    "delete", "remove", "logout", "sign out", "cerrar",
                    "submit", "save", "guardar", "enviar", "confirm",
                    "pay", "pagar", "checkout", "salir", "eliminar",
                    "destroy", "cancel", "borrar", "desactivar",
                    "actualizar", "confirmar", "cerrar sesión",
                ]
                if any(bad in text for bad in excluded_terms):
                    continue
                if any(bad in class_name for bad in excluded_terms):
                    continue
                
                start_url = page.url
                try:
                    loc.click(timeout=1500, force=True)
                except Exception:
                    continue
                
                # Wait briefly to see if URL changes
                page.wait_for_timeout(1000)
                
                new_url = page.url
                if new_url != start_url:
                    normalized = normalize_url(new_url, new_url)
                    if normalized and is_safe_internal_url(normalized, origin):
                        discovered_urls.append(normalized)
                    
                    # Instead of just going back, which can break SPAs, let's try to reload the start_url
                    # if go_back doesn't work or just to be safe.
                    try:
                        page.go_back(timeout=5000)
                    except:
                        page.goto(start_url, wait_until="domcontentloaded", timeout=10000)
                    wait_for_spa(page)
                    
            except Exception:
                pass
    except Exception as e:
        logger.debug("extract_routes_via_clicks error: %s", e)
    return discovered_urls


def discover_routes_authenticated(
    page: Page,
    start_url: str,
    max_pages: int = 10,
) -> list[str]:
    """
    Descubrimiento de rutas para aplicaciones autenticadas con BFS seguro.
    Usa el contexto de la página inicial para abrir nuevas pestañas sin perder la sesión,
    permitiendo descubrir rutas de segundo nivel.
    """
    logger.info(
        "discover_routes_authenticated: starting BFS from %s (max=%d)",
        start_url, max_pages,
    )

    from collections import deque
    queue: deque[str] = deque([page.url])
    visited: set[str] = set()
    discovered: list[str] = []

    # Extraer enlaces de la página principal ya cargada y lista
    initial_links = extract_internal_links(page, start_url)
    clicked_links = extract_routes_via_clicks(page, start_url)
    all_initial_links = list(set(initial_links + clicked_links))
    
    for link in all_initial_links:
        if link not in queue and not is_auth_page_url(link):
            queue.append(link)

    # === Bucle BFS Seguro ===
    while queue and len(discovered) < max_pages:
        current_url = queue.popleft()

        # Normalizar para evitar considerar duplicados como /dashboard y /dashboard/
        normalized = current_url.rstrip("/")
        if normalized in {r.rstrip("/") for r in visited}:
            continue

        visited.add(current_url)

        if is_auth_page_url(current_url):
            continue

        discovered.append(current_url)
        logger.info("Descubierta (Auth BFS): %s (%d/%d)", current_url, len(discovered), max_pages)

        if len(discovered) >= max_pages:
            break

        # Si NO es la página inicial, navegamos a ella en una NUEVA pestaña para no romper la sesión
        if current_url != page.url:
            new_page = None
            try:
                new_page = page.context.new_page()
                
                # Bloquear trackers
                def safe_abort(route):
                    try:
                        route.abort()
                    except:
                        pass
                for pattern in ["**/*google-analytics*", "**/*googletagmanager*", "**/*hotjar*"]:
                    new_page.route(pattern, safe_abort)

                new_page.goto(
                    current_url,
                    wait_until="domcontentloaded",
                    timeout=15000,
                )
                wait_for_spa(new_page)

                # Extraer enlaces de esta sub-página
                new_links = extract_internal_links(new_page, start_url)
                clicked_links = extract_routes_via_clicks(new_page, start_url)
                all_new_links = list(set(new_links + clicked_links))
                
                for link in all_new_links:
                    norm_link = link.rstrip("/")
                    if norm_link not in {r.rstrip("/") for r in visited} and link not in queue:
                        if not is_auth_page_url(link):
                            queue.append(link)
            except Exception as exc:
                logger.debug("Error explorando sub-ruta %s: %s", current_url, exc)
            finally:
                if new_page:
                    try:
                        new_page.close()
                    except:
                        pass

    logger.info(
        "discover_routes_authenticated: finalizó con %d rutas: %s",
        len(discovered), discovered,
    )
    return discovered


def discover_routes(
    page: Page,
    start_url: str,
    max_pages: int = 10,
    timeout_ms: int = 60_000,
) -> list[str]:
    """
    Recorre únicamente rutas internas y autorizadas del mismo dominio.
    Usado para URLs públicas (sin autenticación).
    """

    queue: deque[str] = deque([start_url])
    visited: set[str] = set()
    discovered: list[str] = []

    while queue and len(discovered) < max_pages:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)
        logger.debug("discover_routes processing: %s", current_url)

        try:
            page.goto(
                current_url,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )
            wait_for_spa(page)
            logger.debug("After goto, page.url is: %s", page.url)

        except Exception as e:
            logger.debug("goto failed: %s", e)
            continue

        discovered.append(page.url)
        
        links = extract_internal_links(page, start_url)
        logger.debug("Found internal links via href: %s", links)

        clicked_links = extract_routes_via_clicks(page, start_url)
        logger.debug("Found internal links via clicks: %s", clicked_links)
        
        all_links = list(set(links + clicked_links))

        for link in all_links:
            if link not in visited and link not in queue:
                queue.append(link)

    logger.debug("discover_routes returning: %s", discovered)
    return discovered
