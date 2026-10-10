"""
FrontMind AI Agents API — main.py

Controles de seguridad:
  - CORS restringido a ALLOWED_ORIGINS (env var).
  - X-API-Key obligatoria (falla cerrado si BACKEND_API_KEY no está definida).
  - Identidad del usuario verificada con su access token de Supabase (Bearer):
    el user_id nunca se toma del cliente (evita IDOR en /history y /report).
  - Rate limiting por usuario/IP con bloqueo progresivo y límite de capturas
    concurrentes (core/rate_limit.py).
  - Límites de tamaño en todos los payloads y en la subida de ZIP.
  - Abstract API sólo en el backend (/auth/verify-email).
  - Compresión GZip y cabeceras de seguridad en todas las respuestas.
"""
from __future__ import annotations

import logging
import os
import re
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agents.capture_agent import CaptureAgent
from agents.html_replication_agent import HtmlReplicationAgent
from agents.iso_evaluation_agent import ISOEvaluationAgent
from agents.report_agent import ReportAgent
from core.rate_limit import capture_slot, client_ip, check_rate_limit, rate_limit
from core.security import get_current_user, is_dev_mode, verify_api_key
from services.history_service import add_entry, load_history
from services.progress_service import JOB_ID_PATTERN, read_progress
from services.screenshot_service import take_screenshots_for_multiple_htmls
from services.zip_service import extract_zip_project

# ─────────────────────────────────────────────────────────────────────────────
# Configuración (.env local; en producción las variables vienen del entorno)
# ─────────────────────────────────────────────────────────────────────────────
# utf-8-sig: tolera el BOM que agregan algunos editores/PowerShell en Windows
load_dotenv(encoding="utf-8-sig")

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Límites
# ─────────────────────────────────────────────────────────────────────────────
MAX_HTML_CHARS = 5_000_000          # ~5 MB de HTML por request
MAX_URL_CHARS = 2_048
MAX_SELECTOR_CHARS = 500
MAX_ZIP_BYTES = int(os.environ.get("MAX_ZIP_MB", "20")) * 1024 * 1024
CAPTURE_RETENTION_HOURS = float(os.environ.get("CAPTURE_RETENTION_HOURS", "24"))

# Límites por minuto (por usuario autenticado; por IP si no hay usuario)
RL_GENERAL = 60          # APIs en general
RL_CRITICAL = 5          # capturas Playwright / ZIP (costosas)
RL_EMAIL = 5             # verificación de correo (pre-registro, por IP)
RL_PROGRESS = 40         # polling de progreso


# ─────────────────────────────────────────────────────────────────────────────
# Modelos Pydantic
# ─────────────────────────────────────────────────────────────────────────────

class AuthConfig(BaseModel):
    # "storage_state" se eliminó: aceptaba rutas arbitrarias del servidor.
    mode: Literal["none", "form"] = "none"
    login_url: Optional[str] = Field(default=None, max_length=MAX_URL_CHARS)
    username: Optional[str] = Field(default=None, max_length=320)
    password: Optional[str] = Field(default=None, max_length=1_024)
    username_selector: Optional[str] = Field(default=None, max_length=MAX_SELECTOR_CHARS)
    password_selector: Optional[str] = Field(default=None, max_length=MAX_SELECTOR_CHARS)
    submit_selector: Optional[str] = Field(default=None, max_length=MAX_SELECTOR_CHARS)
    success_url_pattern: Optional[str] = Field(default=None, max_length=MAX_SELECTOR_CHARS)
    success_selector: Optional[str] = Field(default=None, max_length=MAX_SELECTOR_CHARS)


class UrlRequest(BaseModel):
    url: str = Field(max_length=MAX_URL_CHARS)
    auth: Optional[AuthConfig] = None
    max_pages: int = Field(default=10, ge=1, le=50)
    job_id: Optional[str] = Field(default=None, pattern=JOB_ID_PATTERN)


class IsoRequest(BaseModel):
    html: str = Field(max_length=MAX_HTML_CHARS)


class ReportRequest(BaseModel):
    evaluation: dict | list


class HtmlContentRequest(BaseModel):
    html_content: str = Field(max_length=MAX_HTML_CHARS)
    url: str = Field(max_length=MAX_URL_CHARS)
    css_cache: Optional[dict] = None
    cssom_styles: Optional[list] = None


class EmailRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ─────────────────────────────────────────────────────────────────────────────
# Aplicación FastAPI
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not is_dev_mode():
        missing = [v for v in ("SUPABASE_URL", "SUPABASE_ANON_KEY")
                   if not os.environ.get(v, "").strip()]
        if missing:
            logger.error("Variables obligatorias sin configurar: %s — los endpoints responderán 503.",
                         ", ".join(missing))
    purge_old_captures()
    yield


_docs_enabled = os.environ.get("DOCS_ENABLED", "true" if is_dev_mode() else "false").lower() == "true"

app = FastAPI(
    title="FrontMind AI Agents API",
    description=(
        "API para la evaluación técnica automatizada de interfaces frontend "
        "bajo ISO/IEC 25010."
    ),
    version="1.1.0",
    docs_url="/docs" if _docs_enabled else None,
    redoc_url=None,
    openapi_url="/openapi.json" if _docs_enabled else None,
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS, compresión y cabeceras de seguridad
# ─────────────────────────────────────────────────────────────────────────────

_raw_origins = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",   # fallback: solo desarrollo local
)
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip() and o.strip() != "*"]

app.add_middleware(GZipMiddleware, minimum_size=1_024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
    max_age=3_600,
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "cross-origin")
    if request.url.path.startswith("/captures/"):
        # Nombres de archivo únicos e inmutables → cache largo en el navegador.
        response.headers["Cache-Control"] = "private, max-age=86400, immutable"
    else:
        response.headers.setdefault("Cache-Control", "no-store")
    if request.url.scheme == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Directorios y archivos estáticos
# ─────────────────────────────────────────────────────────────────────────────

CAPTURES_DIR = Path("captures")
UPLOADS_DIR = Path("uploads")
CAPTURES_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
Path("extracted_projects_temp").mkdir(exist_ok=True)

# Las capturas se sirven por URL no adivinable (incluye un token aleatorio de
# 128 bits, ver screenshot_worker_impl) porque <img> no puede enviar headers.
app.mount("/captures", StaticFiles(directory=str(CAPTURES_DIR)), name="captures")


def purge_old_captures() -> None:
    """Elimina capturas más antiguas que CAPTURE_RETENTION_HOURS (datos sensibles + disco)."""
    cutoff = time.time() - CAPTURE_RETENTION_HOURS * 3600
    for f in CAPTURES_DIR.glob("*.png"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            pass


# Dependencias comunes: API key → usuario autenticado → rate limit por usuario.
def _protected(scope: str, limit: int) -> list:
    return [Depends(verify_api_key), Depends(get_current_user), Depends(rate_limit(scope, limit))]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {
        "message": "FrontMind AI Agents API funcionando",
        "status": "ok",
        "version": app.version,
    }


# ── Captura ───────────────────────────────────────────────────────────────────

@app.post("/capture/url", dependencies=_protected("capture", RL_CRITICAL))
def capture_url(request: UrlRequest):
    with capture_slot():
        try:
            purge_old_captures()
            agent = CaptureAgent()
            return agent.run(
                url=request.url,
                auth=request.auth.model_dump() if request.auth else None,
                max_pages=request.max_pages,
                job_id=request.job_id,
            )
        except Exception:
            logger.exception("Error en /capture/url")
            raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")


@app.get("/capture/progress", dependencies=_protected("progress", RL_PROGRESS))
def get_capture_progress(job_id: str = Query(..., pattern=JOB_ID_PATTERN)):
    # El job_id es un UUID aleatorio generado por el cliente: sólo quien inició
    # la captura conoce su identificador.
    return {"logs": read_progress(job_id)}


# ── Réplica ───────────────────────────────────────────────────────────────────

@app.post("/replicate/html", dependencies=_protected("capture", RL_CRITICAL))
def replicate_html(request: UrlRequest):
    with capture_slot():
        try:
            capture_agent = CaptureAgent()
            capture_result = capture_agent.run(
                url=request.url,
                auth=request.auth.model_dump() if request.auth else None,
                max_pages=request.max_pages,
                job_id=request.job_id,
            )

            html_agent = HtmlReplicationAgent()

            html_result = html_agent.run(
                html_content=capture_result.get("html_content", ""),
                url=capture_result.get("url", request.url),
                css_cache=capture_result.get("css_cache", {}),
                cssom_styles=capture_result.get("cssom_styles", []),
            )

            interfaces = capture_result.get("interfaces", [])
            for iface in interfaces:
                iface["html_replication"] = html_agent.run(
                    html_content=iface.get("html_content", ""),
                    url=request.url,
                    css_cache=capture_result.get("css_cache", {}),
                    cssom_styles=iface.get("cssom_styles", []),
                )

            return {"capture": capture_result, "html_replication": html_result}
        except Exception:
            logger.exception("Error en /replicate/html")
            raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")


@app.post("/replicate/content", dependencies=_protected("api", RL_GENERAL))
def replicate_content(request: HtmlContentRequest):
    try:
        html_agent = HtmlReplicationAgent()
        html_result = html_agent.run(
            html_content=request.html_content,
            url=request.url,
            css_cache=request.css_cache,
            cssom_styles=request.cssom_styles,
        )
        return {"html_replication": html_result}
    except Exception:
        logger.exception("Error en /replicate/content")
        raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")


# ── Evaluación ────────────────────────────────────────────────────────────────

@app.post("/evaluate/iso", dependencies=_protected("api", RL_GENERAL))
def evaluate_iso(request: IsoRequest):
    try:
        agent = ISOEvaluationAgent()
        return agent.run(request.html)
    except Exception:
        logger.exception("Error en /evaluate/iso")
        raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")


# ── Historial ─────────────────────────────────────────────────────────────────

@app.get("/history", dependencies=[Depends(verify_api_key)])
def get_history(
    user_id: Optional[str] = Depends(get_current_user),
    _rl: None = Depends(rate_limit("api", RL_GENERAL)),
):
    """
    Historial auxiliar del backend (history.json). El historial principal vive
    en Supabase. Sólo devuelve las entradas del usuario autenticado.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Sesión requerida.")
    return [h for h in load_history() if h.get("user_id") == user_id]


# ── Reporte ───────────────────────────────────────────────────────────────────

@app.post("/report/generate", dependencies=[Depends(verify_api_key)])
def generate_report(
    request: ReportRequest,
    user_id: Optional[str] = Depends(get_current_user),
    _rl: None = Depends(rate_limit("api", RL_GENERAL)),
):
    try:
        agent = ReportAgent()
        result = agent.run({"evaluation": request.evaluation})
        add_entry({
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "user_id": user_id,
            "evaluation": request.evaluation,
            "report": result,
        })
        return result
    except Exception:
        logger.exception("Error en /report/generate")
        raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")


# ── ZIP ───────────────────────────────────────────────────────────────────────

def _save_upload_limited(file: UploadFile, destination: Path) -> None:
    """Guarda el archivo subido abortando si supera MAX_ZIP_BYTES."""
    written = 0
    with destination.open("wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            written += len(chunk)
            if written > MAX_ZIP_BYTES:
                raise ValueError(
                    f"El archivo excede el tamaño máximo permitido ({MAX_ZIP_BYTES // (1024 * 1024)} MB)."
                )
            buffer.write(chunk)


@app.post("/upload/zip", dependencies=_protected("capture", RL_CRITICAL))
def upload_zip(file: UploadFile = File(...)):
    original_name = Path(file.filename or "proyecto.zip").name
    if not original_name.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .zip.")

    # Nombre en disco único: evita colisiones entre usuarios concurrentes.
    zip_path = UPLOADS_DIR / f"{uuid.uuid4().hex}.zip"

    with capture_slot():
        try:
            _save_upload_limited(file, zip_path)
            purge_old_captures()

            result = extract_zip_project(str(zip_path))

            htmls_to_capture: dict[str, str] = {}
            combined_html = result.get("combined_html", "")
            if combined_html and result.get("status") != "error":
                htmls_to_capture["combined"] = combined_html

            interfaces = result.get("interfaces", [])
            for iface in interfaces:
                fname = iface.get("file_name", "")
                hcontent = iface.get("html_content", "")
                if fname and hcontent:
                    htmls_to_capture[fname] = hcontent

            captures: list = []
            if htmls_to_capture:
                try:
                    label_prefix = re.sub(r"[^A-Za-z0-9_-]", "_", original_name[:-4])[:20] or "zip"
                    screenshot_results = take_screenshots_for_multiple_htmls(
                        htmls_to_capture, label_prefix=label_prefix
                    )
                    captures = screenshot_results.get("combined", [])
                    for iface in interfaces:
                        fname = iface.get("file_name", "")
                        iface["captures"] = screenshot_results.get(fname, [])
                except Exception:
                    logger.exception("Error capturando screenshots del ZIP")
                    captures = [{"error": "No se pudieron generar capturas.", "device": "all"}]

            return {
                "source_type": "zip",
                "file_name": original_name,
                "status": "processed",
                "extraction": result,
                "captures": captures,
                "html_content": combined_html,
            }
        except ValueError as e:
            # Errores de seguridad / tamaño del ZIP (Zip Slip, Zip Bomb, límite)
            logger.warning("ZIP rechazado: %s", e)
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            logger.exception("Error en /upload/zip")
            raise HTTPException(status_code=500, detail="Error interno al procesar el archivo ZIP.")
        finally:
            try:
                zip_path.unlink(missing_ok=True)
            except OSError:
                pass


# ── Verificación de email (Abstract API en el servidor) ───────────────────────

def _normalize_deliverability(data: dict) -> str:
    """
    Unifica la respuesta de Abstract:
      - Email Validation API:  {"deliverability": "DELIVERABLE"}
      - Email Reputation API:  {"email_deliverability": {"status": "deliverable"}}
    """
    value = data.get("deliverability")
    if not value:
        value = (data.get("email_deliverability") or {}).get("status")
    return str(value or "UNKNOWN").upper()


@app.post("/auth/verify-email", dependencies=[Depends(verify_api_key)])
async def verify_email(payload: EmailRequest, request: Request):
    """
    Proxy hacia Abstract API para verificar entregabilidad de emails.
    Se usa antes del registro (sin sesión), por eso se limita por IP con
    bloqueo progresivo. Sólo se devuelve el veredicto, no el payload externo.
    """
    check_rate_limit(f"verify-email:ip:{client_ip(request)}", RL_EMAIL, 60)

    email = payload.email.strip()
    if not _EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Email inválido.")

    api_key = os.environ.get("ABSTRACT_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Servicio de verificación de correos no configurado.",
        )

    api_url = os.environ.get("ABSTRACT_API_URL", "https://emailreputation.abstractapi.com/v1/")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(api_url, params={"api_key": api_key, "email": email})
        if not r.is_success:
            logger.warning("Abstract API retornó status %s", r.status_code)
            raise HTTPException(status_code=502, detail="Error en el servicio externo de verificación.")
        return {"deliverability": _normalize_deliverability(r.json())}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado al verificar el correo.")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error inesperado en /auth/verify-email")
        raise HTTPException(status_code=500, detail="Error interno al verificar el correo.")
