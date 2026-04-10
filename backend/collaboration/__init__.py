"""Real-time collaboration package."""
from .websocket_manager import WebSocketManager

manager = WebSocketManager()

__all__ = ["manager", "WebSocketManager"]
