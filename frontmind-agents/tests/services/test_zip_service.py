import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core.security import safe_extract_zip
from services import zip_service
from services.zip_service import extract_zip_project


def _make_zip(path: Path, files: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return path


def test_extract_and_filter(tmp_path, monkeypatch):
    monkeypatch.setattr(zip_service, "EXTRACT_BASE_DIR", tmp_path / "extract")
    zip_path = _make_zip(tmp_path / "p.zip", {
        "src/index.html": "<html><body><h1>Hola</h1></body></html>",
        ".git/config": "[core]",
        "node_modules/package/index.js": "module.exports = 1;",
    })

    with patch("services.zip_service._collect_files", wraps=zip_service._collect_files) as collect:
        result = extract_zip_project(str(zip_path))

    assert result["status"] == "extracted"
    collected = collect.call_args[0][0]
    rel = {f["relative_path"].replace("\\", "/") for f in result["files"]}
    assert "src/index.html" in rel
    assert not any(r.startswith((".git", "node_modules")) for r in rel)
    # El directorio temporal por solicitud se elimina siempre
    assert not Path(collected).exists()


def test_extraction_dirs_are_unique(tmp_path, monkeypatch):
    monkeypatch.setattr(zip_service, "EXTRACT_BASE_DIR", tmp_path / "extract")
    zip_path = _make_zip(tmp_path / "p.zip", {"index.html": "<html></html>"})
    seen = []
    with patch("services.zip_service._extract_zip_project",
               side_effect=lambda z, d: seen.append(d) or {"status": "ok"}):
        extract_zip_project(str(zip_path))
        extract_zip_project(str(zip_path))
    assert seen[0] != seen[1]


def test_zip_slip_rejected(tmp_path):
    zip_path = _make_zip(tmp_path / "evil.zip", {"../evil.txt": "x"})
    with pytest.raises(ValueError):
        safe_extract_zip(str(zip_path), str(tmp_path / "out"))


def test_zip_bomb_ratio_rejected(tmp_path):
    zip_path = _make_zip(tmp_path / "bomb.zip", {"a.html": "A" * 5_000_000})
    with pytest.raises(ValueError):
        safe_extract_zip(str(zip_path), str(tmp_path / "out"))


def test_static_site_pages_become_interfaces(tmp_path, monkeypatch):
    """index.html y páginas cortas de un sitio estático son interfaces reales."""
    monkeypatch.setattr(zip_service, "EXTRACT_BASE_DIR", tmp_path / "extract")
    zip_path = _make_zip(tmp_path / "sitio.zip", {
        "src/index.html": "<html><body><main><h1>Mi sitio</h1><a href='c.html'>Contacto</a></main></body></html>",
        "src/contacto.html": "<html><body><form><input type='email'><button>Enviar</button></form></body></html>",
        "src/styles.css": "body{color:#222}",
    })
    result = extract_zip_project(str(zip_path))
    names = sorted(i["file_name"] for i in result["interfaces"])
    assert names == ["contacto.html", "index.html"]


def test_spa_shell_is_skipped():
    shell = "<html><head><script src='main.js'></script></head><body><div id='root'></div></body></html>"
    assert zip_service._is_empty_html_shell(shell) is True
    assert zip_service._is_empty_html_shell("<html><body><form><input></form></body></html>") is False
