"""
agents/capture_agent.py

Cambios aplicados:
  HIGH-05 : Validación SSRF con validate_url() antes de llamar a Playwright.
"""
from __future__ import annotations

import logging

from core.security import validate_url
from services.screenshot_service import take_screenshots

logger = logging.getLogger(__name__)


class CaptureAgent:
    def run(self, url: str, auth: dict = None, max_pages: int = 10):
        if not url:
            return {
                "agent": "CaptureAgent",
                "status": "error",
                "message": "La URL es obligatoria.",
                "url": url,
                "total_interfaces": 0,
                "total_captures": 0,
            }

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        # ── Validación SSRF ───────────────────────────────────────────────
        if not validate_url(url):
            logger.warning("CaptureAgent: URL bloqueada por políticas de seguridad: %s", url)
            return {
                "agent": "CaptureAgent",
                "status": "error",
                "message": (
                    "URL no permitida por políticas de seguridad. "
                    "Solo se aceptan URLs públicas con esquema http/https."
                ),
                "url": url,
                "total_interfaces": 0,
                "total_captures": 0,
            }

        try:
            result = take_screenshots(url=url, auth=auth, max_pages=max_pages)
            return {
                "agent": "CaptureAgent",
                **result,
            }
        except Exception as e:
            logger.exception("CaptureAgent: error al capturar %s", url)
            return {
                "agent": "CaptureAgent",
                "status": "error",
                "message": str(e),
                "url": url,
                "total_interfaces": 0,
                "total_captures": 0,
            }