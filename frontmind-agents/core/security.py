"""
core/security.py — Módulo central de seguridad de FrontMind AI.

Responsabilidades:
  1. verify_api_key  — Dependencia FastAPI para proteger endpoints.
  2. validate_url    — Prevención de SSRF (bloquea IPs privadas/loopback).
  3. safe_extract_zip — Extracción segura contra Zip Slip y Zip Bomb.
"""
from __future__ import annotations

import ipaddress
import logging
import os
import socket
import zipfile
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# 1. API KEY AUTH
# ─────────────────────────────────────────────────────────────────────────────

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(_api_key_header)) -> None:
    """
    Dependencia FastAPI que valida el header X-API-Key.
    Si BACKEND_API_KEY no está configurada en el entorno, emite una advertencia
    y deja pasar (útil en desarrollo local sin .env).
    En producción SIEMPRE configurar BACKEND_API_KEY.
    """
    expected = os.environ.get("BACKEND_API_KEY", "").strip()
    if not expected:
        logger.warning(
            "BACKEND_API_KEY no configurada — todos los requests aceptados. "
            "Configure la variable de entorno en producción."
        )
        return
    if not api_key or api_key != expected:
        logger.warning("Intento de acceso con API key inválida o ausente.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida o ausente.",
        )


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


def validate_url(url: str) -> bool:
    """
    Verifica que una URL sea segura para que Playwright la visite.

    Bloquea:
    - Esquemas distintos a http/https (file://, ftp://, etc.)
    - Hosts en lista negra (localhost, 127.0.0.1, metadata endpoints)
    - IPs privadas RFC-1918, loopback, link-local y reservadas

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

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        return False

    if hostname in _BLOCKED_HOSTS:
        logger.debug("URL bloqueada — host en lista negra: %s", hostname)
        return False

    # Resolver el hostname y verificar que no apunte a una IP interna
    try:
        resolved_ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        if (
            resolved_ip.is_private
            or resolved_ip.is_loopback
            or resolved_ip.is_link_local
            or resolved_ip.is_reserved
            or resolved_ip.is_multicast
        ):
            logger.debug("URL bloqueada — IP interna/reservada: %s → %s", hostname, resolved_ip)
            return False
    except (socket.gaierror, ValueError):
        # Si no se puede resolver, es sospechoso pero no necesariamente un ataque.
        # Dejar que Playwright lo intente; si falla, fallará en la navegación.
        pass

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
    - Zip Bomb: tamaño total descomprimido limitado a 50 MB.
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
        total_uncompressed = sum(m.file_size for m in members)
        if total_uncompressed > _MAX_UNCOMPRESSED_BYTES:
            raise ValueError(
                f"El ZIP excede el límite de tamaño descomprimido "
                f"({total_uncompressed // (1024*1024)} MB > 50 MB)."
            )

        # ── Detección de Zip Slip ─────────────────────────────────────────
        for member in members:
            member_path = (target / member.filename).resolve()
            if not str(member_path).startswith(str(target) + os.sep) and str(member_path) != str(target):
                raise ValueError(
                    f"Ruta insegura detectada en el ZIP: '{member.filename}'. "
                    "El archivo fue rechazado por razones de seguridad."
                )

        # ── Extracción segura ─────────────────────────────────────────────
        zf.extractall(target_dir)
