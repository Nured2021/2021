"""Classroom Manager – manages classroom rooms, members, and roles."""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


def _generate_class_id(prefix: str = "CLASS") -> str:
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(chars) for _ in range(6))
    return f"{prefix}-{suffix}"


@dataclass
class ClassroomMember:
    user_id:   str
    user_name: str
    role:      str     # professor | teacher | student
    joined_at: datetime = field(default_factory=datetime.now)


@dataclass
class Classroom:
    id:          str
    class_id:    str   # human-readable join code, e.g. "CLASS-ABC123"
    name:        str
    subject:     str
    theme:       str   = "default"
    owner_id:    str   = ""
    members:     List[ClassroomMember] = field(default_factory=list)
    created_at:  datetime = field(default_factory=datetime.now)
    is_active:   bool  = True


def _classroom_to_dict(c: Classroom) -> dict:
    return {
        "id":         c.id,
        "class_id":   c.class_id,
        "name":       c.name,
        "subject":    c.subject,
        "theme":      c.theme,
        "owner_id":   c.owner_id,
        "is_active":  c.is_active,
        "created_at": c.created_at.isoformat(),
        "member_count": len(c.members),
        "members": [
            {"user_id": m.user_id, "user_name": m.user_name, "role": m.role}
            for m in c.members
        ],
    }


class ClassroomManager:
    """CRUD for classrooms and membership management."""

    def __init__(self) -> None:
        self.classrooms:       Dict[str, Classroom] = {}
        self._by_class_id:     Dict[str, str]        = {}  # class_id → classroom.id

    def create_classroom(self, name: str, subject: str, owner_id: str,
                          owner_name: str, theme: str = "default") -> Classroom:
        import uuid
        cid      = str(uuid.uuid4())
        class_id = _generate_class_id(subject[:4].upper().replace(" ", "") or "CLASS")
        room = Classroom(id=cid, class_id=class_id, name=name,
                         subject=subject, theme=theme, owner_id=owner_id)
        room.members.append(ClassroomMember(
            user_id=owner_id, user_name=owner_name, role="professor"
        ))
        self.classrooms[cid] = room
        self._by_class_id[class_id] = cid
        return room

    def join_classroom(self, class_id: str, user_id: str,
                        user_name: str, role: str = "student") -> Classroom | None:
        cid  = self._by_class_id.get(class_id)
        room = self.classrooms.get(cid or "")
        if not room:
            return None
        # Don't add duplicate
        for m in room.members:
            if m.user_id == user_id:
                return room
        room.members.append(ClassroomMember(user_id=user_id, user_name=user_name, role=role))
        return room

    def get_classroom(self, classroom_id: str) -> Classroom | None:
        return self.classrooms.get(classroom_id)

    def get_by_class_id(self, class_id: str) -> Classroom | None:
        cid = self._by_class_id.get(class_id)
        return self.classrooms.get(cid or "")

    def list_user_classrooms(self, user_id: str) -> List[dict]:
        return [
            _classroom_to_dict(c)
            for c in self.classrooms.values()
            if any(m.user_id == user_id for m in c.members)
        ]

    def to_dict(self, classroom_id: str) -> dict | None:
        c = self.classrooms.get(classroom_id)
        return _classroom_to_dict(c) if c else None
