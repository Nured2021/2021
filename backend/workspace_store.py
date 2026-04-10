"""Workspace history storage – persists generation records to a JSON file."""

from __future__ import annotations

import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from typing import Any

_STORE_PATH = os.path.join(tempfile.gettempdir(), "workspace_history.json")
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
