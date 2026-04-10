"""FastAPI backend for the Document Generator application."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from main_ai import MainAI

app = FastAPI(title="Document Generator API")

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_STATIC_DIR = Path(__file__).parent / "static"
_STATIC_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

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


class SimpleGenerateRequest(BaseModel):
    prompt: str


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

@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/generate")
async def generate(req: SimpleGenerateRequest) -> dict:
    """Simple endpoint used by the integrated HTML dashboard."""
    try:
        result = _controller.run(req.prompt, doc_type="document")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc

    pdf_filename = Path(result["pdf_path"]).name
    docx_filename = Path(result["docx_path"]).name

    return {
        "content": result["body"],
        "pdf": f"/download/{pdf_filename}",
        "docx": f"/download/{docx_filename}",
    }


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

    # Strip any directory components from the user-supplied name to prevent
    # path traversal before any filesystem operations.
    safe_name = os.path.basename(filename)
    export_dir = os.path.realpath(
        os.path.join(tempfile.gettempdir(), "docgen_exports")
    )
    candidate = os.path.join(export_dir, safe_name)

    # Resolve symlinks and verify the final path is inside the export directory.
    resolved = os.path.realpath(candidate)
    if not resolved.startswith(export_dir + os.sep):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="File not found.")

    media_type = (
        "application/pdf"
        if resolved.endswith(".pdf")
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return FileResponse(resolved, media_type=media_type, filename=safe_name)
