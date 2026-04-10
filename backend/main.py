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
from education_orchestrator import EducationOrchestrator, MODULE_INFO
from export_utils import export_pdf, export_docx

app = FastAPI(title="Easy AI – Document & Education API")

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
_edu = EducationOrchestrator()


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


# Education schemas

class EducationGenerateRequest(BaseModel):
    prompt: str
    module: str | None = None  # auto-detect if omitted


class EducationChatRequest(BaseModel):
    message: str
    module: str | None = None


class EducationUploadMaterialRequest(BaseModel):
    filename: str
    text_content: str
    module: str | None = "student"


class EducationGenerateResponse(BaseModel):
    module: str
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


# ---------------------------------------------------------------------------
# Education endpoints
# ---------------------------------------------------------------------------

@app.get("/education/modules")
def list_education_modules() -> list:
    """Return the list of available education AI modules."""
    return MODULE_INFO


@app.post("/education/generate", response_model=EducationGenerateResponse)
def education_generate(req: EducationGenerateRequest) -> EducationGenerateResponse:
    """Generate structured academic content and export to PDF + DOCX."""
    try:
        result = _edu.generate(req.prompt, module=req.module)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Education generation failed: {exc}") from exc

    pdf_path = export_pdf(result["title"], result["sections"])
    docx_path = export_docx(result["title"], result["sections"])

    pdf_filename = Path(pdf_path).name
    docx_filename = Path(docx_path).name

    return EducationGenerateResponse(
        module=result["module"],
        title=result["title"],
        body=result["body"],
        sections=result["sections"],
        pdf_url=f"/download/{pdf_filename}",
        docx_url=f"/download/{docx_filename}",
    )


@app.post("/education/chat")
def education_chat(req: EducationChatRequest) -> dict:
    """Return a conversational response from the appropriate education module."""
    try:
        return _edu.chat(req.message, module=req.module)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc


@app.post("/education/upload-material")
def education_upload_material(req: EducationUploadMaterialRequest) -> dict:
    """Accept uploaded text content and generate a study guide from it."""
    combined_prompt = (
        f"Summarise and create a study guide for the following material "
        f"from '{req.filename}':\n\n{req.text_content[:4000]}"
    )
    try:
        result = _edu.generate(combined_prompt, module=req.module or "student")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {exc}") from exc

    pdf_path = export_pdf(result["title"], result["sections"])
    docx_path = export_docx(result["title"], result["sections"])

    return {
        "module": result["module"],
        "title": result["title"],
        "body": result["body"],
        "sections": result["sections"],
        "pdf_url": f"/download/{Path(pdf_path).name}",
        "docx_url": f"/download/{Path(docx_path).name}",
    }
