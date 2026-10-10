"""
core/security.py — Módulo central de seguridad de FrontMind AI.

Responsabilidades:
  1. verify_api_key   — Dependencia FastAPI para proteger endpoints (falla cerrado).
     get_current_user — Verifica el access token (JWT) de Supabase del usuario.
  2. validate_url     — Prevención de SSRF (bloquea IPs privadas/loopback).
  3. safe_extract_zip — Extracción segura contra Zip Slip y Zip Bomb.
"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import logging
import os
import socket
import threading
import time
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)


def is_dev_mode() -> bool:
    """Modo desarrollo explícito (FRONTMIND_ENV=development). Producción por defecto."""
    return os.environ.get("FRONTMIND_ENV", "production").strip().lower() == "development"


# ─────────────────────────────────────────────────────────────────────────────
# 1. API KEY AUTH
# ─────────────────────────────────────────────────────────────────────────────

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(_api_key_header)) -> None:
    """
    Dependencia FastAPI que valida el header X-API-Key.

    La clave viaja en el bundle del frontend, así que es una barrera secundaria:
    - Si BACKEND_API_KEY está configurada, se exige (comparación en tiempo constante).
    - Si no lo está, se permite sólo cuando la autenticación de usuarios con
      Supabase está activa (control principal) o en FRONTMIND_ENV=development.
    - Sin ninguna de las dos, falla cerrado.
    """
    expected = os.environ.get("BACKEND_API_KEY", "").strip()
    if not expected:
        supabase_url, anon_key = _supabase_config()
        if is_dev_mode() or (supabase_url and anon_key):
            return
        logger.error("BACKEND_API_KEY no configurada — request rechazado.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio no configurado.",
        )
    if not api_key or not hmac.compare_digest(api_key.encode(), expected.encode()):
        logger.warning("Intento de acceso con API key inválida o ausente.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida o ausente.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 1b. AUTENTICACIÓN DE USUARIO (access token de Supabase)
# ─────────────────────────────────────────────────────────────────────────────
#
# La API key del frontend viaja en el bundle JS, por lo que NO es un secreto.
# La identidad real del usuario se obtiene verificando su access token contra
# GET {SUPABASE_URL}/auth/v1/user, que respeta expiración, logout y revocación.
# El resultado se cachea 60 s por hash del token para no repetir la llamada.

_bearer = HTTPBearer(auto_error=False)
_TOKEN_CACHE_TTL = 60.0
_TOKEN_CACHE_MAX = 2048
_token_cache: dict[str, tuple[float, str]] = {}
_token_cache_lock = threading.Lock()


def _supabase_config() -> tuple[str, str]:
    return (
        os.environ.get("SUPABASE_URL", "").strip().rstrip("/"),
        os.environ.get("SUPABASE_ANON_KEY", "").strip(),
    )


async def _fetch_supabase_user_id(token: str) -> Optional[str]:
    supabase_url, anon_key = _supabase_config()
    cache_key = hashlib.sha256(token.encode()).hexdigest()
    now = time.monotonic()
    with _token_cache_lock:
        cached = _token_cache.get(cache_key)
        if cached and cached[0] > now:
            return cached[1]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"{supabase_url}/auth/v1/user",
                headers={"Authorization": f"Bearer {token}", "apikey": anon_key},
            )
    except httpx.HTTPError:
        logger.warning("No se pudo contactar a Supabase para verificar el token.")
        raise HTTPException(status_code=503, detail="Servicio de autenticación no disponible.")

    if r.status_code != 200:
        return None
    user_id = (r.json() or {}).get("id")
    if not user_id:
        return None

    with _token_cache_lock:
        if len(_token_cache) >= _TOKEN_CACHE_MAX:
            _token_cache.clear()
        _token_cache[cache_key] = (now + _TOKEN_CACHE_TTL, user_id)
    return user_id


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> Optional[str]:
    """
    Devuelve el user_id autenticado.

    - Con SUPABASE_URL y SUPABASE_ANON_KEY configuradas, el Bearer token es
      obligatorio y se verifica contra Supabase.
    - Sin ellas sólo se permite en FRONTMIND_ENV=development (devuelve None).
    """
    supabase_url, anon_key = _supabase_config()
    if not supabase_url or not anon_key:
        if is_dev_mode():
            request.state.user_id = None
            return None
        logger.error("SUPABASE_URL/SUPABASE_ANON_KEY no configuradas — request rechazado.")
        raise HTTPException(status_code=503, detail="Servicio no configurado.")

    if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión requerida.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = await _fetch_supabase_user_id(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.state.user_id = user_id
    return user_id


# ─────────────────────────────────────────────────────────────────────────────
# 2. VALIDACIÓN SSRF DE URLS
# ─────────────────────────────────────────────────────────────────────────────

_ALLOWED_SCHEMES = {"http", "https"}
_BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    # AWS / GCP / Azure metadata endpoints
    "169.254.169.254",
    "metadata.google.internal",
}


def _ip_is_internal(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


@lru_cache(maxsize=1024)
def _resolve_host_allowed(hostname: str) -> bool:
    try:
        return not _ip_is_internal(ipaddress.ip_address(hostname.strip("[]")))
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(hostname, None)
    except (socket.gaierror, UnicodeError):
        # No resoluble: Playwright tampoco podrá conectarse.
        return True
    for info in infos:
        try:
            ip = ipaddress.ip_address(str(info[4][0]).split("%")[0])
        except ValueError:
            return False
        # Se revisan TODAS las IPs resueltas, no sólo la primera.
        if _ip_is_internal(ip):
            return False
    return True


def is_host_allowed(hostname: str) -> bool:
    """True si el host no está en lista negra ni resuelve a IPs internas (cacheado)."""
    hostname = (hostname or "").lower().rstrip(".")
    if not hostname or hostname in _BLOCKED_HOSTS:
        return False
    return _resolve_host_allowed(hostname)


def validate_url(url: str) -> bool:
    """
    Verifica que una URL sea segura para que Playwright la visite.

    Bloquea:
    - Esquemas distintos a http/https (file://, ftp://, etc.)
    - Hosts en lista negra (localhost, 127.0.0.1, metadata endpoints)
    - Hosts que resuelven a IPs privadas, loopback, link-local o reservadas

    Retorna True si la URL es segura, False en caso contrario.
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in _ALLOWED_SCHEMES:
        logger.debug("URL bloqueada — esquema no permitido: %s", url)
        return False

    try:
        hostname = (parsed.hostname or "").lower()
    except ValueError:
        return False

    if not is_host_allowed(hostname):
        logger.debug("URL bloqueada — host interno o en lista negra: %s", hostname)
        return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# 3. EXTRACCIÓN SEGURA DE ZIP
# ─────────────────────────────────────────────────────────────────────────────

_MAX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024   # 50 MB descomprimido
_MAX_FILES = 500
_MAX_COMPRESSION_RATIO = 100                   # zip bomb heuristic


def safe_extract_zip(zip_path: str, target_dir: str) -> None:
    """
    Extrae un ZIP de forma segura verificando:
    - Zip Slip: ningún miembro puede escribir fuera de target_dir.
    - Zip Bomb: tamaño total descomprimido limitado a 50 MB y ratio máximo 100:1.
    - Cantidad de archivos limitada a 500.

    Lanza ValueError si alguna verificación falla.
    """
    target = Path(target_dir).resolve()

    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.infolist()

        # ── Límite de cantidad de archivos ────────────────────────────────
        if len(members) > _MAX_FILES:
            raise ValueError(
                f"El ZIP contiene demasiados archivos ({len(members)} > {_MAX_FILES})."
            )

        # ── Detección de Zip Bomb ─────────────────────────────────────────
        total_uncompressed = sum(int(m.file_size) for m in members)
        if total_uncompressed > _MAX_UNCOMPRESSED_BYTES:
            raise ValueError(
                f"El ZIP excede el límite de tamaño descomprimido "
                f"({total_uncompressed // (1024*1024)} MB > 50 MB)."
            )
        total_compressed = sum(int(m.compress_size) for m in members) or 1
        if total_uncompressed / total_compressed > _MAX_COMPRESSION_RATIO:
            raise ValueError(
                "El ZIP tiene una tasa de compresión sospechosa (posible Zip Bomb)."
            )

        # ── Detección de Zip Slip ─────────────────────────────────────────
        for member in members:
            member_path = (target / member.filename).resolve()
            if member_path != target and target not in member_path.parents:
                raise ValueError(
                    f"Ruta insegura detectada en el ZIP: '{member.filename}'. "
                    "El archivo fue rechazado por razones de seguridad."
                )

        # ── Extracción segura ─────────────────────────────────────────────
        zf.extractall(target_dir)
