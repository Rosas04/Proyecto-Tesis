import json
import os
from pathlib import Path

# Determinar la ruta de data dinámicamente para evitar problemas de permisos en Docker (raíz /)
_project_root = Path(__file__).parent.parent.parent
if _project_root.resolve() == Path("/").resolve() or not os.access(_project_root, os.W_OK):
    _data_dir = Path(__file__).parent.parent / "data"
else:
    _data_dir = _project_root / "data"

HISTORY_FILE = _data_dir / "history.json"

def _ensure_history_file():
    os.makedirs(HISTORY_FILE.parent, exist_ok=True)
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_history():
    _ensure_history_file()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def add_entry(entry: dict):
    _ensure_history_file()
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return entry
