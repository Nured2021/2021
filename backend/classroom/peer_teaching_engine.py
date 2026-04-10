"""Peer-to-Peer Student Teaching Engine – study groups, whiteboard, screen sharing."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from fastapi import WebSocket


class StudyGroupStatus(Enum):
    ACTIVE    = "active"
    INACTIVE  = "inactive"
    COMPLETED = "completed"


@dataclass
class StudyGroup:
    id:                   str
    classroom_id:         str
    name:                 str
    topic:                str
    teacher_student_id:   str
    teacher_student_name: str
    learner_student_ids:  List[str]         = field(default_factory=list)
    status:               StudyGroupStatus  = StudyGroupStatus.ACTIVE
    created_at:           datetime          = field(default_factory=datetime.now)
    session_recording:    str               = ""
    whiteboard_data:      dict              = field(default_factory=lambda: {
                                                "elements": [], "background": "#ffffff"
                                            })
    # WebSocket connections: user_id → ws
    connections:          Dict[str, object] = field(default_factory=dict)


def _group_to_dict(g: StudyGroup) -> dict:
    return {
        "id":                   g.id,
        "classroom_id":         g.classroom_id,
        "name":                 g.name,
        "topic":                g.topic,
        "teacher_student_id":   g.teacher_student_id,
        "teacher_student_name": g.teacher_student_name,
        "learner_student_ids":  g.learner_student_ids,
        "status":               g.status.value,
        "created_at":           g.created_at.isoformat(),
        "session_recording":    g.session_recording,
        "whiteboard_data":      g.whiteboard_data,
    }


class PeerTeachingEngine:
    """Manages study groups, collaborative whiteboard, and screen-share signaling."""

    def __init__(self) -> None:
        self.study_groups:          Dict[str, StudyGroup] = {}
        self.active_screen_shares:  Dict[str, str]        = {}  # group_id → user_id
        self.whiteboard_actions:    Dict[str, List[dict]]  = {}

    # ── Study group lifecycle ──────────────────────────────────────────────

    def create_study_group(self, classroom_id: str, name: str, topic: str,
                            teacher_student_id: str,
                            teacher_student_name: str) -> StudyGroup:
        gid = str(uuid.uuid4())[:8].upper()
        group = StudyGroup(
            id=gid,
            classroom_id=classroom_id,
            name=name,
            topic=topic,
            teacher_student_id=teacher_student_id,
            teacher_student_name=teacher_student_name,
        )
        self.study_groups[gid] = group
        self.whiteboard_actions[gid] = []
        return group

    def join_study_group(self, group_id: str, student_id: str) -> Optional[StudyGroup]:
        grp = self.study_groups.get(group_id)
        if not grp:
            return None
        if student_id not in grp.learner_student_ids and student_id != grp.teacher_student_id:
            grp.learner_student_ids.append(student_id)
        return grp

    def leave_study_group(self, group_id: str, student_id: str) -> bool:
        grp = self.study_groups.get(group_id)
        if grp and student_id in grp.learner_student_ids:
            grp.learner_student_ids.remove(student_id)
            return True
        return False

    # ── Screen sharing ────────────────────────────────────────────────────

    def start_screen_share(self, group_id: str, user_id: str) -> dict:
        self.active_screen_shares[group_id] = user_id
        return {"screen_share_active": True, "teacher_id": user_id, "group_id": group_id}

    def stop_screen_share(self, group_id: str) -> dict:
        self.active_screen_shares.pop(group_id, None)
        return {"screen_share_active": False}

    # ── Whiteboard ────────────────────────────────────────────────────────

    def add_whiteboard_action(self, group_id: str, user_id: str,
                               action_type: str, data: dict) -> dict:
        action = {
            "id":          str(uuid.uuid4())[:8],
            "group_id":    group_id,
            "user_id":     user_id,
            "action_type": action_type,
            "data":        data,
            "timestamp":   datetime.now().isoformat(),
        }
        self.whiteboard_actions.setdefault(group_id, []).append(action)
        grp = self.study_groups.get(group_id)
        if grp:
            if action_type == "clear":
                grp.whiteboard_data["elements"] = []
            else:
                grp.whiteboard_data["elements"].append({"type": action_type, **data})
        return action

    def get_whiteboard_state(self, group_id: str) -> dict:
        grp = self.study_groups.get(group_id)
        return grp.whiteboard_data if grp else {"elements": [], "background": "#ffffff"}

    # ── Session recording ─────────────────────────────────────────────────

    def record_session(self, group_id: str, recording_url: str) -> bool:
        grp = self.study_groups.get(group_id)
        if grp:
            grp.session_recording = recording_url
            return True
        return False

    # ── Queries ───────────────────────────────────────────────────────────

    def get_study_groups_for_classroom(self, classroom_id: str) -> List[dict]:
        return [_group_to_dict(g) for g in self.study_groups.values()
                if g.classroom_id == classroom_id]

    def get_groups_for_student(self, student_id: str) -> List[dict]:
        return [
            _group_to_dict(g) for g in self.study_groups.values()
            if g.teacher_student_id == student_id or student_id in g.learner_student_ids
        ]

    # ── WebSocket hub for a study group ───────────────────────────────────

    async def handle_peer_connection(self, websocket: WebSocket,
                                      classroom_id: str,
                                      user_id: str = "anon",
                                      user_name: str = "Anonymous") -> None:
        """Relay whiteboard, screen-share signaling, and group chat inside a classroom."""
        await websocket.accept()

        async def _broadcast_classroom(msg: dict, exclude: str | None = None) -> None:
            """Broadcast to all groups that belong to this classroom."""
            for grp in self.study_groups.values():
                if grp.classroom_id != classroom_id:
                    continue
                for uid, ws in list(grp.connections.items()):
                    if uid != exclude:
                        try:
                            await ws.send_json(msg)
                        except Exception:
                            pass

        # Register this socket in every active group the user is part of
        for grp in self.study_groups.values():
            if grp.classroom_id == classroom_id and (
                grp.teacher_student_id == user_id or user_id in grp.learner_student_ids
            ):
                grp.connections[user_id] = websocket

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "")
                group_id = data.get("group_id", "")
                grp      = self.study_groups.get(group_id)

                if msg_type == "whiteboard":
                    action = self.add_whiteboard_action(
                        group_id, user_id,
                        data.get("action", "draw"),
                        data.get("data", {}),
                    )
                    if grp:
                        for uid, ws in list(grp.connections.items()):
                            if uid != user_id:
                                try:
                                    await ws.send_json({
                                        "type":   "whiteboard_update",
                                        "action": action,
                                        "user_id": user_id,
                                    })
                                except Exception:
                                    pass

                elif msg_type == "start_screen_share":
                    self.start_screen_share(group_id, user_id)
                    if grp:
                        for uid, ws in list(grp.connections.items()):
                            if uid != user_id:
                                try:
                                    await ws.send_json({
                                        "type":       "screen_share_started",
                                        "teacher_id": user_id,
                                        "group_id":   group_id,
                                    })
                                except Exception:
                                    pass

                elif msg_type == "stop_screen_share":
                    self.stop_screen_share(group_id)
                    if grp:
                        for uid, ws in list(grp.connections.items()):
                            if uid != user_id:
                                try:
                                    await ws.send_json({"type": "screen_share_stopped"})
                                except Exception:
                                    pass

                elif msg_type in ("offer", "answer", "ice_candidate"):
                    # WebRTC signaling for screen-share track
                    target = data.get("target")
                    if grp and target and target in grp.connections:
                        try:
                            await grp.connections[target].send_json({**data, "from": user_id})
                        except Exception:
                            pass

                elif msg_type == "chat":
                    if grp:
                        for uid, ws in list(grp.connections.items()):
                            try:
                                await ws.send_json({
                                    "type":      "chat",
                                    "user_id":   user_id,
                                    "user_name": user_name,
                                    "text":      data.get("text", ""),
                                    "timestamp": datetime.now().isoformat(),
                                })
                            except Exception:
                                pass

                elif msg_type == "join_group":
                    self.join_study_group(group_id, user_id)
                    grp = self.study_groups.get(group_id)
                    if grp:
                        grp.connections[user_id] = websocket
                        # Send whiteboard state to the newcomer
                        try:
                            await websocket.send_json({
                                "type":            "group_state",
                                "group":           _group_to_dict(grp),
                                "whiteboard":      grp.whiteboard_data,
                                "screen_sharing":  self.active_screen_shares.get(group_id),
                            })
                        except Exception:
                            pass
                        await _broadcast_classroom({"type": "group_update"}, exclude=user_id)

        except Exception:
            pass
        finally:
            for grp in self.study_groups.values():
                if grp.classroom_id == classroom_id:
                    grp.connections.pop(user_id, None)
