"""
Verificación previa al despliegue (HuggingFace Spaces / Docker).

Detecta los errores que tumbaron el Space (BUILD_ERROR): archivos de texto
guardados o anexados en UTF-16 por PowerShell (`echo x >> archivo`), BOM,
bytes nulos y líneas de requirements que pip no puede interpretar.

Uso:  python scripts/check_deploy_files.py      (sale con código 1 si hay errores)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEPLOY_FILES = [
    "Dockerfile",
    ".dockerignore",
    ".gitignore",
    ".env.example",
    "README.md",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-agents.txt",
]

# nombre[extras] (operador versión PEP 440)? ; o referencia -r archivo
_VERSION = r"\d+(\.\d+)*(\.\*)?((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?"
_SPEC = rf"(==|>=|<=|~=|!=|>|<)\s*{_VERSION}"
_REQ_LINE = re.compile(
    rf"^(-r\s+\S+|[A-Za-z0-9][A-Za-z0-9._-]*(\[[A-Za-z0-9,._-]+\])?"
    rf"(\s*{_SPEC}(\s*,\s*{_SPEC})*)?)$"
)


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("tiene BOM UTF-8 (guardar como UTF-8 sin BOM)")
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in raw:
        errors.append("contiene UTF-16 o bytes nulos (típico de `echo ... >> archivo` en PowerShell)")
        return errors
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"no es UTF-8 válido: {exc}")
        return errors

    if path.name.startswith("requirements"):
        for n, line in enumerate(text.splitlines(), 1):
            req = line.split("#", 1)[0].strip()
            if req and not _REQ_LINE.match(req):
                errors.append(f"línea {n} no es un requisito válido para pip: {line!r}")
    return errors


def main() -> int:
    failed = False
    for name in DEPLOY_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        for err in check_file(path):
            failed = True
            print(f"[ERROR] {name}: {err}")
    if failed:
        print("Corrige los archivos anteriores antes de desplegar.")
        return 1
    print("Archivos de despliegue OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
