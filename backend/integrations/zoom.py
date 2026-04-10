"""Zoom integration — schedules meetings via the Zoom REST API."""

from __future__ import annotations

import requests


ZOOM_API_BASE = "https://api.zoom.us/v2"


class ZoomIntegration:
    """Create and manage Zoom meetings using a JWT / OAuth2 Bearer token."""

    def __init__(self, access_token: str) -> None:
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
        }

    def create_meeting(self, topic: str, start_time: str,
                       duration: int = 60,
                       agenda: str = "") -> dict:
        """Create a scheduled Zoom meeting and return the response dict.

        Args:
            topic:      Meeting title / topic string.
            start_time: ISO-8601 datetime string, e.g. "2024-12-01T14:00:00Z".
            duration:   Meeting duration in minutes (default 60).
            agenda:     Optional agenda / description string.
        """
        payload = {
            "topic":      topic,
            "type":       2,          # scheduled meeting
            "start_time": start_time,
            "duration":   duration,
            "agenda":     agenda,
            "settings": {
                "join_before_host":  True,
                "waiting_room":      False,
                "meeting_authentication": False,
                "auto_recording":    "none",
            },
        }
        resp = requests.post(
            f"{ZOOM_API_BASE}/users/me/meetings",
            headers=self.headers,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def list_meetings(self) -> list[dict]:
        """Return the user's upcoming scheduled meetings."""
        resp = requests.get(
            f"{ZOOM_API_BASE}/users/me/meetings?type=scheduled",
            headers=self.headers,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("meetings", [])

    def delete_meeting(self, meeting_id: str) -> bool:
        """Cancel / delete a Zoom meeting by ID."""
        resp = requests.delete(
            f"{ZOOM_API_BASE}/meetings/{meeting_id}",
            headers=self.headers,
            timeout=15,
        )
        return resp.status_code == 204
