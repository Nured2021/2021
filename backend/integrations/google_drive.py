"""Google Drive integration — uploads files directly to the user's Drive."""

from __future__ import annotations

import os
from typing import Optional

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    _GOOGLE_AVAILABLE = True
except ImportError:
    _GOOGLE_AVAILABLE = False


class GoogleDriveIntegration:
    """Upload files to Google Drive using an OAuth2 access token."""

    def __init__(self, access_token: str) -> None:
        if not _GOOGLE_AVAILABLE:
            raise RuntimeError(
                "google-api-python-client is not installed. "
                "Add it to requirements.txt and reinstall."
            )
        creds = Credentials(token=access_token)
        self.service = build("drive", "v3", credentials=creds)

    def upload_file(self, file_path: str, filename: str,
                    folder_id: Optional[str] = None) -> str:
        """Upload *file_path* to Drive and return the public view URL.

        *file_path* must be an absolute path that has already been validated
        (canonicalised and confirmed to lie within the server's export directory)
        by the caller before being passed here.
        """
        resolved = os.path.realpath(file_path)
        if not os.path.isfile(resolved):
            raise FileNotFoundError(f"File not found: {resolved}")

        media = MediaFileUpload(resolved, resumable=True)
        file_metadata: dict = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        uploaded = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = uploaded.get("id")

        # Make it readable by anyone with the link
        self.service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        return f"https://drive.google.com/file/d/{file_id}/view"

    def list_files(self, folder_id: Optional[str] = None,
                   limit: int = 20) -> list[dict]:
        """Return a list of recent files in Drive (or a specific folder)."""
        query = f"'{folder_id}' in parents" if folder_id else ""
        result = (
            self.service.files()
            .list(q=query, pageSize=limit, fields="files(id,name,mimeType,webViewLink)")
            .execute()
        )
        return result.get("files", [])
