"""In-memory education chat history, keyed by module."""

from __future__ import annotations

import threading
from typing import Any

_lock = threading.Lock()
_history: dict[str, list[dict[str, str]]] = {}


def add_chat_message(module: str, role: str, content: str) -> None:
    """Append a chat message for the given module."""
    with _lock:
        if module not in _history:
            _history[module] = []
        _history[module].append({"role": role, "content": content})


def get_chat_history(module: str) -> list[dict[str, Any]]:
    """Return the chat history list for *module* (empty list if none)."""
    with _lock:
        return list(_history.get(module, []))


def clear_chat_history(module: str) -> None:
    """Clear the chat history for *module*."""
    with _lock:
        _history.pop(module, None)
