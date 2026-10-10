"""
services/progress_service.py — Progreso de capturas aislado por tarea.

Cada captura escribe su log en progress/<job_id>.log (job_id = UUID generado
por el cliente). Así usuarios concurrentes no ven ni sobrescriben el progreso
de otros, como ocurría con el antiguo progress.txt global.
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Optional

JOB_ID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
_JOB_ID_RE = re.compile(JOB_ID_PATTERN)

PROGRESS_DIR = Path("progress")
_MAX_LINES = 200
_RETENTION_SECONDS = 6 * 3600


def progress_path(job_id: Optional[str]) -> Optional[Path]:
    if not job_id or not _JOB_ID_RE.match(job_id):
        return None
    PROGRESS_DIR.mkdir(exist_ok=True)
    return PROGRESS_DIR / f"{job_id.lower()}.log"


def purge_old_progress() -> None:
    if not PROGRESS_DIR.exists():
        return
    cutoff = time.time() - _RETENTION_SECONDS
    for f in PROGRESS_DIR.glob("*.log"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            pass


def read_progress(job_id: str) -> list[dict]:
    path = progress_path(job_id)
    if path is None or not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").strip().split("\n")
    except OSError:
        return []

    parsed_logs = []
    for line in lines[-_MAX_LINES:]:
        if not line.strip():
            continue
        parts = line.split(" ", 2)
        if len(parts) >= 3:
            parsed_logs.append({
                "time": parts[0],
                "type": parts[1].strip("[]"),
                "message": parts[2],
            })
    return parsed_logs
