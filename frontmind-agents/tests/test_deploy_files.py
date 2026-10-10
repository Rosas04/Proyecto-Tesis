"""Evita volver a desplegar archivos corruptos (causa del BUILD_ERROR del Space)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_deploy_files", Path(__file__).resolve().parent.parent / "scripts" / "check_deploy_files.py"
)
check_deploy_files = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_deploy_files)


def test_repo_deploy_files_are_clean():
    assert check_deploy_files.main() == 0


def test_detects_powershell_utf16_append(tmp_path):
    # Reproduce el archivo desplegado: "lxml==5.3.0" + "openai" anexado en UTF-16
    f = tmp_path / "requirements.txt"
    f.write_bytes(b"httpx==0.27.2\nlxml==5.3.0" + "openai\r\n".encode("utf-16-le") + b"\nlangchain\n")
    assert check_deploy_files.check_file(f)


def test_detects_bom_and_invalid_requirement(tmp_path):
    f = tmp_path / "requirements.txt"
    f.write_bytes(b"\xef\xbb\xbffastapi==0.143.0\nlxml==5.3.0openai\n")
    errors = check_deploy_files.check_file(f)
    assert any("BOM" in e for e in errors)
    assert any("línea 2" in e for e in errors)


def test_accepts_valid_requirements(tmp_path):
    f = tmp_path / "requirements.txt"
    f.write_text("# comentario\n-r base.txt\nuvicorn[standard]==0.54.0\nopenai>=1.40,<4\npip-audit\n",
                 encoding="utf-8")
    assert check_deploy_files.check_file(f) == []
