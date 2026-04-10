"""Google Drive integration — uploads files directly to the user's Drive."""

from __future__ import annotations

import os
import tempfile
from typing import Optional

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    _GOOGLE_AVAILABLE = True
except ImportError:
    _GOOGLE_AVAILABLE = False

# The only directory on this server from which files may be uploaded.
_EXPORT_DIR = os.path.realpath(os.path.join(tempfile.gettempdir(), "docgen_exports"))


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

        Only files located within the server's known export directory are
        permitted.  The path is canonicalised and checked before use to
        prevent path-traversal attacks.
        """
        resolved = os.path.realpath(file_path)

        # Enforce that the file lies within the designated export directory
        if not (resolved.startswith(_EXPORT_DIR + os.sep) or resolved == _EXPORT_DIR):
            raise PermissionError(
                "Only files from the server export directory may be uploaded to Drive."
            )
        if not os.path.isfile(resolved):
            raise FileNotFoundError(f"File not found: {resolved}")

        # Use the resolved, validated path — never the raw user-supplied value
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

    def upload_by_name(self, filename: str,
                        drive_name: Optional[str] = None,
                        folder_id: Optional[str] = None) -> str:
        """Upload a file from the server's export directory by its basename only.

        This is the preferred call from HTTP endpoints because the path is
        constructed entirely from a server-controlled constant (_EXPORT_DIR)
        combined with the validated basename — no user-supplied path reaches
        any filesystem API.
        """
        import re
        # Only allow safe filename characters; strip any path components.
        safe_name = os.path.basename(filename)
        if not safe_name or not re.match(r'^[\w\-. ]+$', safe_name):
            raise ValueError(f"Unsafe filename: {filename!r}")
        # Construct the full path entirely from the server-side constant
        full_path = os.path.join(_EXPORT_DIR, safe_name)
        return self.upload_file(full_path, drive_name or safe_name, folder_id)

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
