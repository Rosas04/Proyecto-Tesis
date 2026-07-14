import sys
import re

with open(r'c:\Users\Home\Desktop\Proyecto-Tesis\frontmind-agents\services\screenshot_worker_impl.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace the take_screenshots function and the imports at the top
new_imports = """import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from playwright.sync_api import sync_playwright

from services.auth_service import (
    normalize_auth_config,
    perform_form_login,
    save_storage_state,
)
from services.route_discovery_service import discover_routes

CAPTURES_DIR = Path("captures")

VIEWPORTS = [
    {
        "device": "desktop",
        "width": 1366,
        "height": 768,
    },
    {
        "device": "tablet",
        "width": 768,
        "height": 1024,
    },
    {
        "device": "mobile",
        "width": 390,
        "height": 844,
    },
]

def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"https?://", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:80] or "interface"

def collect_dom_metrics(page) -> dict[str, int]:
    return page.evaluate(
        \"\"\"
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
        \"\"\"
    )

def extract_cssom_styles(page) -> list[str]:
    try:
        extracted = page.evaluate(\"\"\"() => {
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
        }\"\"\")
        if isinstance(extracted, list):
            return extracted
    except Exception:
        pass
    return []

"""

new_take_screenshots = """def take_screenshots(
    url: str,
    auth: dict[str, Any] | None = None,
    max_pages: int = 10,
) -> dict[str, Any]:
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    auth_config = normalize_auth_config(auth)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    results: list[dict[str, Any]] = []
    routes: list[str] = []
    global_css_cache = {}

    def handle_response(response):
        try:
            if response.request.resource_type == "stylesheet":
                url_str = response.url
                if url_str not in global_css_cache:
                    global_css_cache[url_str] = response.text()
        except Exception:
            pass

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        storage_state = auth_config.get("storage_state_path")

        context_args: dict[str, Any] = {
            "ignore_https_errors": False,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        if (
            auth_config["mode"] == "storage_state"
            and storage_state
            and Path(storage_state).exists()
        ):
            context_args["storage_state"] = storage_state

        discovery_context = browser.new_context(**context_args)
        discovery_page = discovery_context.new_page()

        try:
            if auth_config["mode"] == "form":
                perform_form_login(
                    discovery_page,
                    auth_config,
                )

                generated_state_path = (
                    f"playwright/.auth/session_{timestamp}.json"
                )

                save_storage_state(
                    discovery_context,
                    generated_state_path,
                )

                storage_state = generated_state_path

            discovery_page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            discovery_page.wait_for_timeout(1_500)
            
            # Expand SPA dropdowns to ensure hidden links are in the DOM before discovering
            try:
                discovery_page.evaluate(\"\"\"() => {
                    const toggles = document.querySelectorAll('button, [role="button"], [aria-expanded], [aria-haspopup], .menu-item, [class*="dropdown"], [class*="nav"], [class*="menu"]');
                    toggles.forEach(t => {
                        try {
                            const text = (t.innerText || '').toLowerCase();
                            if(text.includes('logout') || text.includes('sign out') || text.includes('cerrar sesion') || text.includes('exit')) return;
                            if(text.includes('delete') || text.includes('remove') || text.includes('eliminar')) return;
                            t.click();
                        } catch(e) {}
                    });
                }\"\"\")
                discovery_page.wait_for_timeout(1500)
            except:
                pass

            routes = discover_routes(
                discovery_page,
                start_url=discovery_page.url,
                max_pages=max_pages,
            )

        finally:
            discovery_context.close()

        if not routes:
            routes = [url]

        for route_index, route_url in enumerate(routes, start=1):
            route_result: dict[str, Any] = {
                "route_index": route_index,
                "url": route_url,
                "name": slugify(route_url),
                "file_name": slugify(route_url) + ".html",
                "relative_path": urlparse(route_url).path,
                "status": "pending",
                "html_content": "",
                "cssom_styles": [],
                "dom_metrics": {},
                "captures": [],
                "errors": [],
            }

            for viewport in VIEWPORTS:
                context_options: dict[str, Any] = {
                    "viewport": {
                        "width": viewport["width"],
                        "height": viewport["height"],
                    },
                    "device_scale_factor": 1,
                    "user_agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                }

                if storage_state and Path(storage_state).exists():
                    context_options["storage_state"] = storage_state

                context = browser.new_context(**context_options)
                page = context.new_page()
                page.on("response", handle_response)

                try:
                    page.goto(
                        route_url,
                        wait_until="domcontentloaded",
                        timeout=60_000,
                    )

                    page.wait_for_timeout(1_500)
                    
                    try:
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(300)
                        page.evaluate("window.scrollTo(0, 0)")
                        page.wait_for_timeout(300)
                    except: pass

                    if viewport["device"] == "desktop":
                        route_result["html_content"] = page.content()
                        route_result["cssom_styles"] = extract_cssom_styles(page)
                        route_result["dom_metrics"] = collect_dom_metrics(page)
                        route_result["title"] = page.title()

                    file_name = (
                        f"{timestamp}_"
                        f"{route_index:02d}_"
                        f"{slugify(route_url)}_"
                        f"{viewport['device']}.png"
                    )

                    file_path = CAPTURES_DIR / file_name

                    page.screenshot(
                        path=str(file_path),
                        full_page=True,
                    )

                    route_result["captures"].append(
                        {
                            "device": viewport["device"],
                            "width": viewport["width"],
                            "height": viewport["height"],
                            "file_name": file_name,
                            "file_path": str(file_path),
                            "public_url": (
                                f"{api_base_url.rstrip('/')}/"
                                f"captures/{file_name}"
                            ),
                            "success": True,
                        }
                    )

                except Exception as exc:
                    route_result["errors"].append(
                        {
                            "device": viewport["device"],
                            "message": str(exc),
                        }
                    )

                finally:
                    context.close()

            successful = sum(
                1
                for capture in route_result["captures"]
                if capture.get("success")
            )

            route_result["successful_captures"] = successful
            route_result["status"] = (
                "completed" if successful > 0 else "error"
            )

            results.append(route_result)

        browser.close()
        
    main_page_data = results[0] if results else None
    html_content = main_page_data["html_content"] if main_page_data else ""
    captures = main_page_data["captures"] if main_page_data else []
    cssom_styles = main_page_data["cssom_styles"] if main_page_data else []

    return {
        "source_type": "authenticated_url",
        "status": "completed",
        "start_url": url,
        "url": url,
        "authentication_mode": auth_config["mode"],
        "authenticated_state_created": bool(storage_state),
        "routes_discovered": len(routes),
        "interfaces": results,
        "total_interfaces": len(results),
        "total_captures": sum(
            len(interface["captures"])
            for interface in results
        ),
        "captured_at": timestamp,
        "html_content": html_content,
        "captures": captures,
        "css_cache": global_css_cache,
        "cssom_styles": cssom_styles,
    }
"""

start_idx = content.find("def take_screenshots")
end_idx = content.find("def take_screenshots_from_html")

final_content = new_imports + "\n" + new_take_screenshots + "\n\n" + content[end_idx:]

with open(r'c:\Users\Home\Desktop\Proyecto-Tesis\frontmind-agents\services\screenshot_worker_impl.py', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Done")
