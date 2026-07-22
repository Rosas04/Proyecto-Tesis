from __future__ import annotations

from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag

from playwright.sync_api import Page
import sys


EXCLUDED_PATH_WORDS = {
    "logout",
    "signout",
    "cerrar-sesion",
    "delete",
    "remove",
    "eliminar",
    "download",
}

def wait_for_spa(page: Page):
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass
    try:
        page.locator("#root, main, [role='main']").first.wait_for(state="visible", timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(2000)
    
    try:
        page.evaluate("""
            const selectorsToRemove = [
                'iframe', 
                '[id*="cookie"]', '[class*="cookie"]', 
                '[role="dialog"]',
                '.spinner', '.loader', '.skeleton', '[aria-busy="true"]'
            ];
            selectorsToRemove.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => el.remove());
            });
        """)
    except Exception:
        pass


def normalize_url(base_url: str, candidate: str) -> str | None:
    if not candidate:
        return None

    absolute = urljoin(base_url, candidate)
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

    if parsed_candidate.netloc != parsed_origin.netloc:
        return False

    lower_path = parsed_candidate.path.lower()

    if any(word in lower_path for word in EXCLUDED_PATH_WORDS):
        return False

    return True


def extract_internal_links(
    page: Page,
    origin: str,
) -> list[str]:
    raw_links = page.locator("a[href]").evaluate_all(
        """
        elements => elements.map(element => element.getAttribute('href'))
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
    discovered_urls = []
    try:
        # Find potential navigation elements
        locators = page.locator("button, [role='button'], [role='link'], [class*='nav'], [class*='menu'], [class*='sidebar'], [class*='flow-item'], [class*='tab'], [class*='link'], li").all()
        # Limit to first 5 to avoid excessive clicking and massive time delays
        locators = locators[:5]
        
        for loc in locators:
            try:
                if not loc.is_visible():
                    continue
                text = (loc.inner_text() or "").lower()
                class_name = (loc.get_attribute("class") or "").lower()
                
                # Exclude destructive actions
                excluded_terms = ["delete", "remove", "logout", "sign out", "cerrar", "submit", "save", "guardar", "enviar", "confirm", "pay", "checkout", "salir", "eliminar", "destroy"]
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
                page.wait_for_timeout(800)
                
                new_url = page.url
                if new_url != start_url:
                    normalized = normalize_url(new_url, new_url)
                    if normalized and is_safe_internal_url(normalized, origin):
                        discovered_urls.append(normalized)
                    
                    # Go back to continue clicking
                    page.go_back(timeout=10000)
                    wait_for_spa(page)
                    
            except Exception:
                pass
    except Exception as e:
        print(f"[DEBUG] extract_routes_via_clicks error: {e}", file=sys.stderr)
    return discovered_urls

def discover_routes(
    page: Page,
    start_url: str,
    max_pages: int = 10,
    timeout_ms: int = 60_000,
) -> list[str]:
    """
    Recorre únicamente rutas internas y autorizadas del mismo dominio.
    """

    queue: deque[str] = deque([start_url])
    visited: set[str] = set()
    discovered: list[str] = []

    while queue and len(discovered) < max_pages:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"[DEBUG] discover_routes processing: {current_url}", file=sys.stderr)

        try:
            page.goto(
                current_url,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )
            wait_for_spa(page)
            print(f"[DEBUG] After goto, page.url is: {page.url}", file=sys.stderr)

        except Exception as e:
            print(f"[DEBUG] goto failed: {e}", file=sys.stderr)
            continue

        discovered.append(page.url)
        
        links = extract_internal_links(page, start_url)
        print(f"[DEBUG] Found internal links via href: {links}", file=sys.stderr)

        for link in links:
            if link not in visited and link not in queue:
                queue.append(link)

    print(f"[DEBUG] discover_routes returning: {discovered}", file=sys.stderr)
    return discovered
