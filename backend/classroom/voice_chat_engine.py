"""Voice Chat Engine – real-time audio communication for classrooms via WebRTC signaling."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class VoiceSession:
    classroom_id:    str
    session_id:      str
    active_speakers: Set[str]         = field(default_factory=set)
    muted_users:     Set[str]         = field(default_factory=set)
    connections:     Dict[str, tuple] = field(default_factory=dict)   # user_id → (ws, name)
    is_recording:    bool             = False
    recording_path:  str              = ""
    started_at:      datetime         = field(default_factory=datetime.now)


class VoiceChatEngine:
    """
    WebRTC signaling server for classroom voice chat.

    Browser peers exchange SDP offers/answers and ICE candidates through this
    server.  Actual audio is handled peer-to-peer in the browser via WebRTC;
    the server only relays signaling messages and tracks mute/recording state.
    """

    ICE_SERVERS = [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
    ]

    def __init__(self) -> None:
        self.active_sessions: Dict[str, VoiceSession] = {}
        self.transcriptions:  Dict[str, List[dict]]   = {}

    # ── Session management ────────────────────────────────────────────────

    def get_or_create_session(self, classroom_id: str) -> VoiceSession:
        if classroom_id not in self.active_sessions:
            ts = int(datetime.now().timestamp())
            self.active_sessions[classroom_id] = VoiceSession(
                classroom_id=classroom_id,
                session_id=f"voice_{classroom_id}_{ts}",
                recording_path=f"/recordings/voice_{classroom_id}_{ts}.webm",
            )
        return self.active_sessions[classroom_id]

    def join_voice(self, classroom_id: str, user_id: str, user_name: str) -> dict:
        """Return WebRTC configuration so the browser can start dialling."""
        session = self.get_or_create_session(classroom_id)
        return {
            "session_id":  session.session_id,
            "user_id":     user_id,
            "user_name":   user_name,
            "muted":       user_id in session.muted_users,
            "ice_servers": self.ICE_SERVERS,
        }

    # ── Mute control ──────────────────────────────────────────────────────

    def mute_user(self, classroom_id: str, user_id: str) -> None:
        session = self.get_or_create_session(classroom_id)
        session.muted_users.add(user_id)
        session.active_speakers.discard(user_id)

    def unmute_user(self, classroom_id: str, user_id: str) -> None:
        session = self.get_or_create_session(classroom_id)
        session.muted_users.discard(user_id)

    # ── Recording ─────────────────────────────────────────────────────────

    def start_recording(self, classroom_id: str) -> dict:
        session = self.get_or_create_session(classroom_id)
        session.is_recording = True
        return {"recording": True, "path": session.recording_path}

    def stop_recording(self, classroom_id: str) -> dict:
        session = self.get_or_create_session(classroom_id)
        session.is_recording = False
        return {"recording": False, "saved_path": session.recording_path}

    # ── Transcriptions ────────────────────────────────────────────────────

    def add_transcription(self, classroom_id: str, user_id: str,
                          user_name: str, text: str) -> None:
        self.transcriptions.setdefault(classroom_id, []).append({
            "user_id":   user_id,
            "user_name": user_name,
            "text":      text,
            "timestamp": datetime.now().isoformat(),
        })

    def get_transcriptions(self, classroom_id: str) -> List[dict]:
        return self.transcriptions.get(classroom_id, [])

    # ── WebSocket signaling hub ───────────────────────────────────────────

    async def handle_connection(self, websocket: WebSocket,
                                 classroom_id: str,
                                 user_id: str = "anonymous",
                                 user_name: str = "Anonymous") -> None:
        """Accept WS connection and relay WebRTC signaling messages."""
        await websocket.accept()
        session = self.get_or_create_session(classroom_id)
        session.connections[user_id] = (websocket, user_name)

        # Announce the new participant
        await self._broadcast(session, {
            "type":       "peer_joined",
            "user_id":    user_id,
            "user_name":  user_name,
            "ice_servers": self.ICE_SERVERS,
            "speakers":   list(session.active_speakers),
            "muted":      list(session.muted_users),
        }, exclude=user_id)

        # Send init to the joining user
        await websocket.send_json({
            "type":       "init",
            "session_id": session.session_id,
            "ice_servers": self.ICE_SERVERS,
            "peers":      [
                {"user_id": uid, "user_name": nm}
                for uid, (_, nm) in session.connections.items()
                if uid != user_id
            ],
            "muted":       user_id in session.muted_users,
            "is_recording": session.is_recording,
        })

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "")

                if msg_type == "offer":
                    await self._relay_to(session, data["target"], {
                        "type": "offer", "sdp": data["sdp"], "from": user_id,
                    })
                elif msg_type == "answer":
                    await self._relay_to(session, data["target"], {
                        "type": "answer", "sdp": data["sdp"], "from": user_id,
                    })
                elif msg_type == "ice_candidate":
                    await self._relay_to(session, data["target"], {
                        "type": "ice_candidate", "candidate": data["candidate"], "from": user_id,
                    })
                elif msg_type == "speaking":
                    session.active_speakers.add(user_id)
                    await self._broadcast(session, {
                        "type": "speaker_update",
                        "speakers": [
                            {"id": uid, "name": session.connections[uid][1]}
                            for uid in session.active_speakers
                            if uid in session.connections
                        ],
                    })
                elif msg_type == "stopped_speaking":
                    session.active_speakers.discard(user_id)
                    await self._broadcast(session, {
                        "type": "speaker_update",
                        "speakers": [
                            {"id": uid, "name": session.connections[uid][1]}
                            for uid in session.active_speakers
                            if uid in session.connections
                        ],
                    })
                elif msg_type == "mute":
                    self.mute_user(classroom_id, user_id)
                    await self._broadcast(session, {"type": "user_muted", "user_id": user_id})
                elif msg_type == "unmute":
                    self.unmute_user(classroom_id, user_id)
                    await self._broadcast(session, {"type": "user_unmuted", "user_id": user_id})
                elif msg_type == "transcription":
                    self.add_transcription(classroom_id, user_id, user_name, data.get("text", ""))
                    await self._broadcast(session, {
                        "type":      "transcription",
                        "user_id":   user_id,
                        "user_name": user_name,
                        "text":      data.get("text", ""),
                        "timestamp": datetime.now().isoformat(),
                    })
                elif msg_type == "start_recording":
                    self.start_recording(classroom_id)
                    await self._broadcast(session, {"type": "recording_started"})
                elif msg_type == "stop_recording":
                    info = self.stop_recording(classroom_id)
                    await self._broadcast(session, {"type": "recording_stopped", **info})

        except Exception:
            pass
        finally:
            session.connections.pop(user_id, None)
            session.active_speakers.discard(user_id)
            await self._broadcast(session, {
                "type": "peer_left", "user_id": user_id, "user_name": user_name,
            })

    async def _broadcast(self, session: VoiceSession, message: dict,
                          exclude: str | None = None) -> None:
        for uid, (ws, _) in list(session.connections.items()):
            if uid != exclude:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    async def _relay_to(self, session: VoiceSession,
                         target_user_id: str, message: dict) -> None:
        if target_user_id in session.connections:
            ws, _ = session.connections[target_user_id]
            try:
                await ws.send_json(message)
            except Exception:
                pass
