"""WebSocket manager for real-time document collaboration."""

from __future__ import annotations

import json
import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages active WebSocket connections per document and broadcasts edits."""

    def __init__(self) -> None:
        # document_id → list of (websocket, user_id) tuples
        self.active_connections: Dict[str, List[tuple]] = {}
        # document_id → current content string
        self.document_content: Dict[str, str] = {}
        # document_id → list of {user_id, name, color, position} cursor states
        self.cursors: Dict[str, Dict[str, dict]] = {}

    # ── Connection lifecycle ──────────────────────────────────────────────

    async def connect(self, websocket: WebSocket, document_id: str, user_id: str,
                      user_name: str = "Anonymous") -> None:
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
            self.cursors[document_id] = {}
        self.active_connections[document_id].append((websocket, user_id))

        # Assign a cursor colour
        colours = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
                   "#ec4899", "#06b6d4", "#84cc16"]
        colour = colours[len(self.active_connections[document_id]) % len(colours)]
        self.cursors[document_id][user_id] = {
            "user_id": user_id,
            "name":    user_name,
            "color":   colour,
            "position": 0,
        }

        # Send current document content to the newly connected user
        current = self.document_content.get(document_id, "")
        await websocket.send_json({
            "type":    "init",
            "content": current,
            "cursors": list(self.cursors[document_id].values()),
            "users":   self._active_users(document_id),
        })

        # Notify others that someone joined
        await self.broadcast(document_id, {
            "type":  "user_joined",
            "user":  user_id,
            "name":  user_name,
            "color": colour,
            "users": self._active_users(document_id),
        }, sender=websocket)

    async def disconnect(self, websocket: WebSocket, document_id: str, user_id: str) -> None:
        conns = self.active_connections.get(document_id, [])
        self.active_connections[document_id] = [
            (ws, uid) for ws, uid in conns if ws is not websocket
        ]
        if document_id in self.cursors:
            self.cursors[document_id].pop(user_id, None)
        # Notify others
        await self.broadcast(document_id, {
            "type":  "user_left",
            "user":  user_id,
            "users": self._active_users(document_id),
        })

    # ── Messaging ──────────────────────────────────────────────────────────

    async def broadcast(self, document_id: str, message: dict,
                        sender: WebSocket | None = None) -> None:
        """Send *message* to all connections on the document except *sender*."""
        for ws, _uid in list(self.active_connections.get(document_id, [])):
            if ws is not sender:
                try:
                    await ws.send_json(message)
                except Exception:
                    logger.debug("Broadcast failed for a connection; it may have closed.")

    async def handle_edit(self, document_id: str, user_id: str,
                          content: str, cursor: int | None,
                          sender: WebSocket) -> None:
        self.document_content[document_id] = content
        if document_id in self.cursors and user_id in self.cursors[document_id]:
            self.cursors[document_id][user_id]["position"] = cursor or 0
        await self.broadcast(document_id, {
            "type":    "update",
            "content": content,
            "user":    user_id,
            "cursor":  cursor,
        }, sender=sender)

    async def handle_cursor(self, document_id: str, user_id: str,
                             position: int, sender: WebSocket) -> None:
        if document_id in self.cursors and user_id in self.cursors[document_id]:
            self.cursors[document_id][user_id]["position"] = position
        await self.broadcast(document_id, {
            "type":     "cursor",
            "user":     user_id,
            "position": position,
        }, sender=sender)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _active_users(self, document_id: str) -> list:
        seen: set = set()
        result = []
        for _ws, uid in self.active_connections.get(document_id, []):
            if uid not in seen:
                seen.add(uid)
                cursor_info = self.cursors.get(document_id, {}).get(uid, {})
                result.append({
                    "user_id": uid,
                    "name":    cursor_info.get("name", uid),
                    "color":   cursor_info.get("color", "#3b82f6"),
                })
        return result

    def get_content(self, document_id: str) -> str:
        return self.document_content.get(document_id, "")

    def active_user_count(self, document_id: str) -> int:
        return len(self.active_connections.get(document_id, []))
