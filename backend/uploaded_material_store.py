"""Uploaded material storage – persists uploaded file records to a JSON file."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from typing import Any

_STORE_PATH = os.path.join(tempfile.gettempdir(), "uploaded_materials.json")
_lock = threading.Lock()


def _load() -> list[dict[str, Any]]:
    if not os.path.isfile(_STORE_PATH):
        return []
    try:
        with open(_STORE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list[dict[str, Any]]) -> None:
    with open(_STORE_PATH, "w", encoding="utf-8") as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)


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
