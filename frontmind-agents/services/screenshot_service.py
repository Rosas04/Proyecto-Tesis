import os
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright


def take_screenshots(url: str):
    api_base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    output_dir = Path("captures")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    viewports = [
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

    captures = []
    html_content = ""

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
                viewport={
                    "width": item["width"],
                    "height": item["height"],
                },
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )

            try:
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

                page.wait_for_timeout(3000)

                if item["device"] == "desktop":
                    html_content = page.content()

                file_name = f"{item['device']}_{timestamp}.png"
                file_path = output_dir / file_name

                page.screenshot(
                    path=str(file_path),
                    full_page=True,
                )

                captures.append(
                    {
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "file_name": file_name,
                        "file_path": str(file_path),
                        "public_url": f"{api_base_url.rstrip('/')}/captures/{file_name}",
                    }
                )

            except Exception as e:
                captures.append(
                    {
                        "device": item["device"],
                        "width": item["width"],
                        "height": item["height"],
                        "error": str(e),
                    }
                )

            finally:
                page.close()

        browser.close()

    return {
        "html_content": html_content,
        "captures": captures,
        "total_captures": len(captures),
        "captured_at": timestamp,
    }