import os
import sys
import json
import subprocess
from pathlib import Path

def _run_worker(request: dict) -> dict:
    """Helper to run the screenshot worker in a clean subprocess to prevent asyncio loop errors."""
    cli_path = Path(__file__).parent / "screenshot_cli.py"
    
    # We use venv python if available, otherwise fallback to sys.executable
    venv_python = Path(__file__).parent.parent / "venv" / "Scripts" / "python.exe"
    python_exe = str(venv_python) if venv_python.exists() else sys.executable
    
    proc = subprocess.run(
        [python_exe, str(cli_path)],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=600
    )
    
    if proc.returncode == 0:
        return json.loads(proc.stdout)
    else:
        # Raise the error so it can be handled by callers
        error_msg = proc.stderr or "Error running screenshot worker"
        raise RuntimeError(error_msg)


def take_screenshots(url: str, auth: dict = None, max_pages: int = 10, credentials: dict = None) -> dict:
    auth_data = auth if auth is not None else credentials
    return _run_worker({
        "action": "url",
        "url": url,
        "auth": auth_data,
        "max_pages": max_pages
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