"""FastAPI backend for the Document Generator application."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main_ai import MainAI
from education_orchestrator import EducationOrchestrator, MODULE_INFO
from export_utils import export_pdf, export_docx
from workspace_store import save_workspace_item, list_workspace_items
from education_memory import add_chat_message, get_chat_history
from uploaded_material_store import save_uploaded_material, list_uploaded_materials

app = FastAPI(title="Easy AI – Document & Education API")

_STATIC_DIR = Path(__file__).parent / "static"
_STATIC_DIR.mkdir(exist_ok=True)

# Path to the compiled React frontend (built with: cd frontend && npm run build)
_DIST_DIR = Path(__file__).parent.parent / "frontend" / "dist"

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# Serve Vite's hashed asset bundles (JS / CSS / images) as /assets/...
if (_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(_DIST_DIR / "assets")), name="frontend_assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_controller = MainAI()
_edu = EducationOrchestrator()

# MIME types for generated file extensions
_MIME = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    prompt: str
    doc_type: str = "document"  # "doc" | "pdf" | "slides" | "excel" | "document" | "presentation"


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
    docx_url: str | None = None
    pptx_url: str | None = None
    xlsx_url: str | None = None


# Education schemas

class EducationGenerateRequest(BaseModel):
    prompt: str
    module: str | None = None  # auto-detect if omitted


class EducationChatRequest(BaseModel):
    message: str
    module: str | None = None


class EducationGenerateResponse(BaseModel):
    module: str
    title: str
    body: str
    sections: list[SectionOut]
    pdf_url: str
    docx_url: str


# ---------------------------------------------------------------------------
# Intent classifier for /api/build
# ---------------------------------------------------------------------------

_INTENT_MAP: dict[str, list[str]] = {
    "presentation": [
        "slide", "slides", "pitch deck", "presentation", "powerpoint", "keynote",
    ],
    "spreadsheet": [
        "budget", "spreadsheet", "excel", "table", "tracker", "sheet", "financial model",
        "invoice", "expense", "salary",
    ],
    "education": [
        "course", "lesson", "quiz", "exam", "professor", "teacher", "student",
        "study guide", "assignment", "syllabus", "lecture", "curriculum",
    ],
    "research": [
        "summarize", "summarise", "research", "analyze", "analyse", "abstract",
        "literature review", "paper review", "findings",
    ],
    "document": [
        "letter", "proposal", "report", "resume", "cv", "contract", "policy",
        "memo", "agreement", "business case", "document",
    ],
}


def _classify_intent(prompt: str) -> str:
    """Return the most likely intent label for *prompt* using keyword matching."""
    text = prompt.lower()
    for intent, keywords in _INTENT_MAP.items():
        if any(kw in text for kw in keywords):
            return intent
    return "document"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _url(path: str | None) -> str | None:
    if not path:
        return None
    return f"/download/{Path(path).name}"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, response_model=None, include_in_schema=False)
def home():
    """Serve the React SPA shell from the production build."""
    index = _DIST_DIR / "index.html"
    if index.is_file():
        return FileResponse(str(index))
    return HTMLResponse(
        "<h1>Frontend not built.</h1>"
        "<p>Run: <code>cd frontend &amp;&amp; npm run build</code></p>",
        status_code=503,
    )


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

    return {
        "content": result["body"],
        "pdf":  _url(result.get("pdf_path")),
        "docx": _url(result.get("docx_path")),
    }


@app.post("/generate-document", response_model=GenerateResponse)
def generate_document(req: GenerateRequest) -> GenerateResponse:
    try:
        result = _controller.run(req.prompt, doc_type=req.doc_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc

    pdf_url  = _url(result.get("pdf_path"))
    docx_url = _url(result.get("docx_path"))
    pptx_url = _url(result.get("pptx_path"))
    xlsx_url = _url(result.get("xlsx_path"))

    # Persist to workspace history
    save_workspace_item({
        "prompt":   req.prompt,
        "doc_type": req.doc_type,
        "mode":     "document",
        "title":    result["title"],
        "preview":  result["body"][:300],
        "pdf_url":  pdf_url,
        "docx_url": docx_url,
        "pptx_url": pptx_url,
        "xlsx_url": xlsx_url,
    })

    return GenerateResponse(
        title=result["title"],
        body=result["body"],
        sections=result["sections"],
        pdf_url=pdf_url,
        docx_url=docx_url,
        pptx_url=pptx_url,
        xlsx_url=xlsx_url,
    )


@app.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    import tempfile

    safe_name = os.path.basename(filename)
    export_dir = os.path.realpath(
        os.path.join(tempfile.gettempdir(), "docgen_exports")
    )
    candidate = os.path.join(export_dir, safe_name)
    resolved = os.path.realpath(candidate)
    if not resolved.startswith(export_dir + os.sep):
        raise HTTPException(status_code=403, detail="Access denied.")
    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="File not found.")

    ext = Path(resolved).suffix.lower()
    media_type = _MIME.get(ext, "application/octet-stream")
    return FileResponse(resolved, media_type=media_type, filename=safe_name)


# ---------------------------------------------------------------------------
# Unified build endpoint — auto-routes to the correct engine
# ---------------------------------------------------------------------------

class BuildRequest(BaseModel):
    prompt: str
    mode: str = "auto"  # "auto" | "document" | "presentation" | "spreadsheet" | "education" | "research"


@app.post("/api/build")
def api_build(req: BuildRequest) -> dict:
    """Single entry-point that classifies the prompt and delegates to the
    correct generation engine, then returns a normalised response."""
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=422, detail="Prompt must not be empty.")

    intent: str = req.mode if req.mode != "auto" else _classify_intent(req.prompt)
    timestamp = datetime.now(tz=timezone.utc).isoformat()

    try:
        if intent == "presentation":
            raw = _controller.run(req.prompt, doc_type="slides")
            type_str = "presentation"
            engine = "presentation_ai"
            module_str = None
        elif intent == "spreadsheet":
            raw = _controller.run(req.prompt, doc_type="excel")
            type_str = "spreadsheet"
            engine = "excel_ai"
            module_str = None
        elif intent in ("education", "research"):
            edu_module = "professor" if intent == "education" else "student"
            edu_result = _edu.generate(req.prompt, module=edu_module)
            raw = dict(edu_result)
            raw["pdf_path"]  = export_pdf(raw["title"], raw["sections"])
            raw["docx_path"] = export_docx(raw["title"], raw["sections"])
            type_str = intent
            engine = f"education_{edu_module}_ai"
            module_str = raw.get("module") or edu_module
        else:
            raw = _controller.run(req.prompt, doc_type="document")
            type_str = "document"
            engine = "document_ai"
            module_str = None
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Build failed: {exc}") from exc

    pdf_url  = _url(raw.get("pdf_path"))
    docx_url = _url(raw.get("docx_path"))
    pptx_url = _url(raw.get("pptx_path"))
    xlsx_url = _url(raw.get("xlsx_path"))

    # Persist to workspace history
    save_workspace_item({
        "prompt":   req.prompt,
        "mode":     type_str,
        "module":   module_str,
        "title":    raw["title"],
        "preview":  raw["body"][:300],
        "pdf_url":  pdf_url,
        "docx_url": docx_url,
        "pptx_url": pptx_url,
        "xlsx_url": xlsx_url,
    })

    return {
        "success":  True,
        "type":     type_str,
        "title":    raw["title"],
        "prompt":   req.prompt,
        "body":     raw["body"],
        "sections": raw["sections"],
        "module":   module_str,
        "pdf_url":  pdf_url,
        "docx_url": docx_url,
        "pptx_url": pptx_url,
        "xlsx_url": xlsx_url,
        "meta": {
            "engine":    engine,
            "intent":    intent,
            "timestamp": timestamp,
        },
    }


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------

@app.get("/workspace/history")
def workspace_history() -> list:
    """Return the full workspace generation history."""
    return list_workspace_items()


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

    pdf_path  = export_pdf(result["title"], result["sections"])
    docx_path = export_docx(result["title"], result["sections"])

    pdf_filename  = Path(pdf_path).name
    docx_filename = Path(docx_path).name

    # Persist to workspace history
    save_workspace_item({
        "prompt":   req.prompt,
        "mode":     "education",
        "module":   result["module"],
        "title":    result["title"],
        "preview":  result["body"][:300],
        "pdf_url":  f"/download/{pdf_filename}",
        "docx_url": f"/download/{docx_filename}",
    })

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
    """Return a conversational response from the appropriate education module,
    persisting the conversation in memory."""
    module = req.module or "student"

    # Store user message
    add_chat_message(module, "user", req.message)

    try:
        response = _edu.chat(req.message, module=module)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc

    reply = response.get("reply") or response.get("content") or str(response)

    # Store assistant reply
    add_chat_message(module, "assistant", reply)

    return {
        "module":  module,
        "reply":   reply,
        "history": get_chat_history(module),
    }


@app.post("/education/upload-material")
async def education_upload_material(
    file: UploadFile = File(...),
    module: str = "student",
) -> dict:
    """Accept an uploaded file, persist it, and generate a study guide."""
    try:
        raw = await file.read()
        text_content = raw.decode("utf-8", errors="replace")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read file: {exc}") from exc

    # Persist the uploaded material record
    save_uploaded_material(
        filename=file.filename or "unknown",
        module=module,
        extracted_text=text_content,
    )

    combined_prompt = (
        f"Summarise and create a study guide for the following material "
        f"from '{file.filename}':\n\n{text_content[:4000]}"
    )
    try:
        result = _edu.generate(combined_prompt, module=module or "student")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {exc}") from exc

    pdf_path  = export_pdf(result["title"], result["sections"])
    docx_path = export_docx(result["title"], result["sections"])

    return {
        "filename": file.filename,
        "saved":    True,
        "module":   result["module"],
        "title":    result["title"],
        "body":     result["body"],
        "sections": result["sections"],
        "pdf_url":  f"/download/{Path(pdf_path).name}",
        "docx_url": f"/download/{Path(docx_path).name}",
    }


@app.get("/education/materials")
def list_materials() -> list:
    """Return list of all previously uploaded materials."""
    return list_uploaded_materials()


# ---------------------------------------------------------------------------
# SPA catch-all — must be the LAST route registered
# Serves any path that isn't an API endpoint as the React index.html so that
# client-side routing (React Router / direct URL entry) works correctly.
# ---------------------------------------------------------------------------

@app.get("/{full_path:path}", response_class=HTMLResponse, response_model=None, include_in_schema=False)
def serve_spa(full_path: str):
    """Serve static files from the React build, falling back to index.html."""
    if _DIST_DIR.is_dir():
        # Try to serve an actual file from the dist root (favicon, icons, etc.)
        candidate = _DIST_DIR / full_path
        if candidate.is_file():
            return FileResponse(str(candidate))
        # For all other paths (SPA client-side routes) return the shell
        index = _DIST_DIR / "index.html"
        if index.is_file():
            return FileResponse(str(index))
    return HTMLResponse(
        "<h1>Frontend not built.</h1>"
        "<p>Run: <code>cd frontend &amp;&amp; npm run build</code></p>",
        status_code=503,
    )
