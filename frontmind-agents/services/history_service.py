import json
import os
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent.parent / "data" / "history.json"

def _ensure_history_file():
    os.makedirs(HISTORY_FILE.parent, exist_ok=True)
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_history():
    _ensure_history_file()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def add_entry(entry: dict):
    _ensure_history_file()
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return entry
