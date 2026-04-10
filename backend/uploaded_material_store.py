"""Uploaded material storage – persists uploaded file records to a JSON file."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow override via environment variable; default to a data/ dir beside this file.
_DEFAULT_DIR = Path(__file__).parent / "data"
_DATA_DIR = Path(os.environ.get("EASY_AI_DATA_DIR", str(_DEFAULT_DIR)))
_DATA_DIR.mkdir(parents=True, exist_ok=True)

_STORE_PATH = _DATA_DIR / "uploaded_materials.json"
_lock = threading.Lock()


def _load() -> list[dict[str, Any]]:
    if not _STORE_PATH.is_file():
        return []
    try:
        return json.loads(_STORE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list[dict[str, Any]]) -> None:
    _STORE_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def save_uploaded_material(
    filename: str,
    module: str,
    extracted_text: str,
) -> dict[str, Any]:
    """Save an uploaded material record and return it with id/timestamp."""
    with _lock:
        items = _load()
        record = {
            "id": len(items) + 1,
            "filename": filename,
            "module": module,
            "extracted_text": extracted_text[:4000],  # cap stored text
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        items.insert(0, record)
        _save(items)
    return record


def list_uploaded_materials() -> list[dict[str, Any]]:
    """Return all saved uploaded materials (newest first)."""
    with _lock:
        return _load()
