"""FastAPI backend for the Document Generator application."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from main_ai import MainAI

app = FastAPI(title="Document Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_controller = MainAI()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str
    doc_type: str = "document"  # "document" | "presentation" | "excel"


class SectionOut(BaseModel):
    heading: str
    content: str


class GenerateResponse(BaseModel):
    title: str
    body: str
    sections: list[SectionOut]
    pdf_url: str
    docx_url: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/generate-document", response_model=GenerateResponse)
def generate_document(req: GenerateRequest) -> GenerateResponse:
    try:
        result = _controller.run(req.prompt, doc_type=req.doc_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc

    pdf_filename = Path(result["pdf_path"]).name
    docx_filename = Path(result["docx_path"]).name

    return GenerateResponse(
        title=result["title"],
        body=result["body"],
        sections=result["sections"],
        pdf_url=f"/download/{pdf_filename}",
        docx_url=f"/download/{docx_filename}",
    )


@app.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    import tempfile

    export_dir = os.path.join(tempfile.gettempdir(), "docgen_exports")
    file_path = os.path.join(export_dir, filename)

    # Security: ensure the resolved path stays inside export_dir
    if not os.path.realpath(file_path).startswith(os.path.realpath(export_dir)):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    media_type = (
        "application/pdf"
        if filename.endswith(".pdf")
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return FileResponse(file_path, media_type=media_type, filename=filename)
