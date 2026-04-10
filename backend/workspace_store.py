"""Workspace history storage – persists generation records to a JSON file."""

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

_STORE_PATH = _DATA_DIR / "workspace_history.json"
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


def save_workspace_item(item: dict[str, Any]) -> dict[str, Any]:
    """Append *item* to the workspace history and return it with an id/timestamp."""
    with _lock:
        items = _load()
        record = {
            "id": len(items) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **item,
        }
        items.insert(0, record)  # newest first
        _save(items)
    return record


def list_workspace_items() -> list[dict[str, Any]]:
    """Return the full workspace history (newest first)."""
    with _lock:
        return _load()
