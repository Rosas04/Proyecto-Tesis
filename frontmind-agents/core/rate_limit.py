"""
core/rate_limit.py — Rate limiting en memoria para FrontMind AI.

- Ventana deslizante por clave (usuario autenticado o IP).
- Bloqueo progresivo: cada vez que una clave excede su límite, el bloqueo
  se duplica (60 s, 120 s, 240 s… hasta 1 h). Se reinicia tras 1 h sin abusos.
- Semáforo global para limitar capturas Playwright concurrentes.

Nota: el estado es por proceso. Con un solo worker de uvicorn (despliegue
actual en HuggingFace Spaces) los límites son exactos; con varios workers o
réplicas habría que mover este estado a Redis.
"""
from __future__ import annotations

import math
import os
import threading
import time
from collections import deque
from typing import Callable

from fastapi import HTTPException, Request

_lock = threading.Lock()
_hits: dict[str, deque[float]] = {}
_blocked_until: dict[str, float] = {}
_strikes: dict[str, tuple[int, float]] = {}

_BASE_BLOCK_SECONDS = 60
_MAX_BLOCK_SECONDS = 3600
_STRIKE_RESET_SECONDS = 3600
_MAX_KEYS = 50_000


def client_ip(request: Request) -> str:
    """
    IP del cliente. Sólo se confía en X-Forwarded-For si TRUST_PROXY_HEADERS=true
    (HuggingFace Spaces / Render ponen un proxy delante).
    """
    if os.environ.get("TRUST_PROXY_HEADERS", "false").lower() == "true":
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _identity(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    return f"user:{user_id}" if user_id else f"ip:{client_ip(request)}"


def check_rate_limit(key: str, limit: int, window_seconds: int = 60) -> None:
    """Lanza HTTP 429 si `key` superó `limit` requests en la ventana."""
    now = time.monotonic()
    with _lock:
        if len(_hits) > _MAX_KEYS:
            _hits.clear()
            _blocked_until.clear()

        until = _blocked_until.get(key, 0.0)
        if until > now:
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Intente más tarde.",
                headers={"Retry-After": str(math.ceil(until - now))},
            )

        q = _hits.setdefault(key, deque())
        while q and q[0] <= now - window_seconds:
            q.popleft()

        if len(q) >= limit:
            strikes, last = _strikes.get(key, (0, 0.0))
            if now - last > _STRIKE_RESET_SECONDS:
                strikes = 0
            strikes += 1
            _strikes[key] = (strikes, now)
            block = min(_BASE_BLOCK_SECONDS * (2 ** (strikes - 1)), _MAX_BLOCK_SECONDS)
            _blocked_until[key] = now + block
            q.clear()
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Intente más tarde.",
                headers={"Retry-After": str(block)},
            )

        q.append(now)


def rate_limit(scope: str, limit: int, window_seconds: int = 60) -> Callable:
    """
    Dependencia FastAPI. Debe declararse DESPUÉS de get_current_user para que
    el límite sea por usuario; si no hay usuario se limita por IP.
    """
    def dependency(request: Request) -> None:
        check_rate_limit(f"{scope}:{_identity(request)}", limit, window_seconds)
    return dependency


def reset_rate_limits() -> None:
    """Sólo para tests."""
    with _lock:
        _hits.clear()
        _blocked_until.clear()
        _strikes.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Concurrencia de capturas (Playwright consume ~300-500 MB por navegador)
# ─────────────────────────────────────────────────────────────────────────────

MAX_CONCURRENT_CAPTURES = max(1, int(os.environ.get("MAX_CONCURRENT_CAPTURES", "2")))
_capture_semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_CAPTURES)


class capture_slot:
    """Context manager: ocupa un slot de captura o responde 503 si no hay."""

    def __enter__(self):
        if not _capture_semaphore.acquire(blocking=False):
            raise HTTPException(
                status_code=503,
                detail="El servidor está procesando otras capturas. Intente en unos minutos.",
                headers={"Retry-After": "60"},
            )
        return self

    def __exit__(self, *exc):
        _capture_semaphore.release()
        return False
