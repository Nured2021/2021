"""
UPLOAD MEMORY — Stores and organizes all uploaded materials
Documents, code, notes, images, extracted text, processed chunks.
"""

class UploadMemory:
    def __init__(self):
        self.uploads = []

    def add_upload(self, upload):
        self.uploads.append(upload)

    def get_uploads(self, filetype=None):
        if filetype:
            return [u for u in self.uploads if u.get("type") == filetype]
        return self.uploads






