import os
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

def take_screenshots(url: str):
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    viewports = [
        {"device": "desktop", "width": 1366, "height": 768},
        {"device": "tablet",  "width": 768,  "height": 1024},
        {"device": "mobile",  "width": 390,  "height": 844},
    ]

    captures = []
    html_content = ""
    css_cache = {}
    cssom_styles = []

    def handle_response(response):
        try:
            if response.request.resource_type == "stylesheet":
                url_str = response.url
                if url_str not in css_cache:
                    css_cache[url_str] = response.text()
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        for item in viewports:
            page = browser.new_page(
                viewport={"width": item["width"], "height": item["height"]},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            page.on("response", handle_response)

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Scroll down and back up to trigger lazy loading
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(1000)
                except Exception:
                    pass

                page.wait_for_timeout(2000)

                if item["device"] == "desktop":
                    html_content = page.content()
                    try:
                        extracted = page.evaluate("""() => {
                            const styles = [];
                            for (const sheet of document.styleSheets) {
                                try {
                                    if (!sheet.href) {
                                        const rules = sheet.cssRules || sheet.rules;
                                        let content = "";
                                        for (const rule of rules) {
                                            content += rule.cssText + "\\n";
                                        }
                                        if (content.trim()) {
                                            styles.push(content);
                                        }
                                    }
                                } catch (e) {
                                    // Ignore CORS errors
                                }
                            }
                            return styles;
                        }""")
                        if isinstance(extracted, list):
                            for style_str in extracted:
                                if style_str not in cssom_styles:
                                    cssom_styles.append(style_str)
                    except Exception:
                        pass

                file_name = f"{item['device']}_{timestamp}.png"
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
        "html_content": html_content,
        "captures": captures,
        "total_captures": len(captures),
        "captured_at": timestamp,
        "css_cache": css_cache,
        "cssom_styles": cssom_styles,
    }


def take_screenshots_from_html(html_content: str, label: str = "zip"):
    """Generate viewport screenshots from raw HTML using Playwright set_content()."""
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    viewports = [
        {"device": "desktop", "width": 1366, "height": 768},
        {"device": "tablet",  "width": 768,  "height": 1024},
        {"device": "mobile",  "width": 390,  "height": 844},
    ]

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

        for item in viewports:
            page = browser.new_page(
                viewport={"width": item["width"], "height": item["height"]},
            )

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
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    viewports = [
        {"device": "desktop", "width": 1366, "height": 768},
        {"device": "tablet",  "width": 768,  "height": 1024},
        {"device": "mobile",  "width": 390,  "height": 844},
    ]

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

            for item in viewports:
                page = browser.new_page(
                    viewport={"width": item["width"], "height": item["height"]},
                )

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
