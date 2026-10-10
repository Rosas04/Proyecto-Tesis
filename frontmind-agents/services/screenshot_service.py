import json
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

WORKER_TIMEOUT_SECONDS = 1800


def _run_worker(request: dict) -> dict:
    """Helper to run the screenshot worker in a clean subprocess to prevent asyncio loop errors."""
    cli_path = Path(__file__).parent / "screenshot_cli.py"

    try:
        proc = subprocess.run(
            [sys.executable, str(cli_path)],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=WORKER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("La captura excedió el tiempo máximo permitido.")

    if proc.returncode == 0:
        if proc.stderr:
            logger.warning("Screenshot worker stderr: %s", proc.stderr[-2000:])
        return json.loads(proc.stdout)

    # Raise the error so it can be handled by callers
    logger.error("Screenshot worker falló: %s", (proc.stderr or "")[-2000:])
    raise RuntimeError("Error ejecutando el worker de capturas.")


def take_screenshots(url: str, auth: dict = None, max_pages: int = 10, credentials: dict = None,
                     job_id: str = None) -> dict:
    auth_data = auth if auth is not None else credentials
    return _run_worker({
        "action": "url",
        "url": url,
        "auth": auth_data,
        "max_pages": max_pages,
        "job_id": job_id,
    })


def take_screenshots_from_html(html_content: str, label: str = "zip") -> dict:
    return _run_worker({
        "action": "html",
        "html": html_content,
        "label": label
    })


def take_screenshots_for_multiple_htmls(htmls: dict, label_prefix: str = "zip") -> dict:
    return _run_worker({
        "action": "multiple",
        "htmls": htmls,
        "label_prefix": label_prefix
    })
