"""FastAPI backend for Easy AI – the fully integrated multi-module AI workspace."""

from __future__ import annotations

import io
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main_ai import MainAI, detect_module, _MODULE_NAMES
from education_orchestrator import EducationOrchestrator, MODULE_INFO
from export_utils import export_pdf, export_docx
from workspace_store import save_workspace_item, list_workspace_items
from education_memory import add_chat_message, get_chat_history
from uploaded_material_store import save_uploaded_material, list_uploaded_materials
from upload_ai import UploadAI

app = FastAPI(title="Easy AI – Full Multi-Module AI Workspace")

_STATIC_DIR = Path(__file__).parent / "static"
_STATIC_DIR.mkdir(exist_ok=True)
_DIST_DIR = Path(__file__).parent.parent / "frontend" / "dist"

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
if (_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(_DIST_DIR / "assets")), name="frontend_assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_brain   = MainAI()
_edu     = EducationOrchestrator()
_upload  = UploadAI()

_MIME = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


# ---------------------------------------------------------------------------
# Templates library (pre-built prompts for every module)
# ---------------------------------------------------------------------------

TEMPLATES: list[dict] = [
    # Documents
    {"id": "doc-proposal",   "module": "document",   "label": "Business Proposal",        "prompt": "Write a professional business proposal for an AI-powered education platform"},
    {"id": "doc-report",     "module": "document",   "label": "Executive Report",          "prompt": "Create an executive report on the current state of remote work in tech companies"},
    {"id": "doc-plan",       "module": "document",   "label": "Project Plan",              "prompt": "Write a comprehensive project plan for launching a new mobile application"},
    {"id": "doc-letter",     "module": "document",   "label": "Professional Letter",       "prompt": "Write a professional letter requesting a meeting to discuss a partnership opportunity"},
    {"id": "doc-contract",   "module": "document",   "label": "Service Contract",          "prompt": "Draft a service agreement contract for a software development project"},
    {"id": "doc-resume",     "module": "document",   "label": "Professional Resume",       "prompt": "Create a professional resume for a senior software engineer with 10 years experience"},
    # Business
    {"id": "biz-plan",       "module": "business",   "label": "Full Business Plan",        "prompt": "Create a complete business plan for a SaaS startup in the education technology market"},
    {"id": "biz-pitch",      "module": "business",   "label": "Investor Pitch Deck",       "prompt": "Write an investor pitch deck for a Series A fundraise for an AI platform startup"},
    {"id": "biz-swot",       "module": "business",   "label": "SWOT Analysis",             "prompt": "Conduct a SWOT analysis for a mid-sized consulting firm entering the AI market"},
    {"id": "biz-marketing",  "module": "business",   "label": "Marketing Strategy",        "prompt": "Create a digital marketing strategy for a B2B SaaS product targeting HR professionals"},
    {"id": "biz-financial",  "module": "business",   "label": "Financial Projections",     "prompt": "Build a 3-year financial model and revenue forecast for a subscription software business"},
    # Research
    {"id": "res-litreview",  "module": "research",   "label": "Literature Review",         "prompt": "Write a literature review on the impact of artificial intelligence on higher education"},
    {"id": "res-paper",      "module": "research",   "label": "Research Paper",            "prompt": "Write a full research paper on the effectiveness of online learning vs classroom learning"},
    {"id": "res-abstract",   "module": "research",   "label": "Research Abstract",         "prompt": "Write a structured research abstract on machine learning applications in healthcare"},
    {"id": "res-proposal",   "module": "research",   "label": "Research Proposal",         "prompt": "Write a PhD research proposal on the psychological effects of social media on adolescents"},
    # Analytics
    {"id": "ana-kpi",        "module": "analytics",  "label": "KPI Dashboard Report",      "prompt": "Create a KPI dashboard report for a customer success team with metrics on retention and NPS"},
    {"id": "ana-trends",     "module": "analytics",  "label": "Trend Analysis",            "prompt": "Write a trend analysis report on e-commerce growth in emerging markets"},
    {"id": "ana-insights",   "module": "analytics",  "label": "Data Insights Report",      "prompt": "Create a data insights report on employee performance and productivity metrics"},
    # Content
    {"id": "con-blog",       "module": "content",    "label": "SEO Blog Post",             "prompt": "Write an SEO-optimized blog post about the top 10 benefits of artificial intelligence for small businesses"},
    {"id": "con-social",     "module": "content",    "label": "Social Media Pack",         "prompt": "Create a social media content pack for LinkedIn, Twitter, and Instagram about productivity tips"},
    {"id": "con-email",      "module": "content",    "label": "Email Campaign",            "prompt": "Write a 3-email drip campaign for a new online course launch targeting working professionals"},
    {"id": "con-press",      "module": "content",    "label": "Press Release",             "prompt": "Write a press release announcing the launch of an innovative AI-powered HR platform"},
    # Education
    {"id": "edu-lesson",     "module": "teacher",    "label": "Lesson Plan",               "prompt": "Create a detailed lesson plan on photosynthesis for 8th grade biology students"},
    {"id": "edu-syllabus",   "module": "professor",  "label": "University Syllabus",       "prompt": "Design a complete university syllabus for an undergraduate course in Organisational Behaviour"},
    {"id": "edu-quiz",       "module": "exam",       "label": "Quiz with Answer Key",      "prompt": "Create a 10-question quiz with answer key on the French Revolution for high school students"},
    {"id": "edu-study",      "module": "student",    "label": "Study Guide",               "prompt": "Create a comprehensive study guide with flashcards for the topic of Newton's Laws of Motion"},
    {"id": "edu-course",     "module": "course",     "label": "Course Curriculum",         "prompt": "Build a 10-week course curriculum on Data Science for beginners with no programming experience"},
    # Legal
    {"id": "leg-case",       "module": "court",      "label": "Legal Case Package",        "prompt": "Prepare a full legal case package including opening statement, legal analysis and closing argument for an employment discrimination case"},
    {"id": "leg-contract",   "module": "court",      "label": "Service Contract",          "prompt": "Draft a comprehensive service contract agreement for a digital marketing agency and its client"},
    {"id": "leg-brief",      "module": "court",      "label": "Legal Brief",               "prompt": "Write a legal brief for a contract dispute case where one party failed to deliver agreed services"},
    # Simulation
    {"id": "sim-interview",  "module": "simulation", "label": "Job Interview Prep",        "prompt": "Create a mock job interview simulation for a Senior Product Manager role at a tech company"},
    {"id": "sim-cover",      "module": "simulation", "label": "Cover Letter",              "prompt": "Write a compelling cover letter for a Data Scientist position at a leading AI research company"},
    # Excel / Slides
    {"id": "xls-budget",     "module": "excel",      "label": "Annual Budget",             "prompt": "Create an annual budget spreadsheet for a tech startup with 20 employees"},
    {"id": "xls-tracker",    "module": "excel",      "label": "Project Tracker",           "prompt": "Build a project tracker spreadsheet with milestones, owners, due dates and status"},
    {"id": "ppt-business",   "module": "slides",     "label": "Business Presentation",     "prompt": "Create a 8-slide business presentation on the future of artificial intelligence in healthcare"},
    {"id": "ppt-pitch",      "module": "slides",     "label": "Investor Deck",             "prompt": "Build a 7-slide investor pitch deck for a Series A fundraise in an edtech startup"},
    # Other
    {"id": "int-check",      "module": "integrity",  "label": "Integrity Review",          "prompt": "Perform an academic integrity review and citation guide for a research paper on climate change"},
    {"id": "lng-translate",  "module": "multilingual","label": "Translation Package",      "prompt": "Translate a business proposal about sustainable energy solutions into French and Spanish"},
    {"id": "adm-schedule",   "module": "admin",       "label": "Event Schedule",           "prompt": "Create a full administrative schedule and task tracker for a 3-day academic conference"},
]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class BuildRequest(BaseModel):
    prompt: str
    module: str = "auto"

class SimpleGenerateRequest(BaseModel):
    prompt: str

class SectionOut(BaseModel):
    heading: str
    content: str

class GenerateRequest(BaseModel):
    prompt: str
    doc_type: str = "document"

class GenerateResponse(BaseModel):
    title: str
    body: str
    sections: list[SectionOut]
    pdf_url: str
    docx_url: str | None = None
    pptx_url: str | None = None
    xlsx_url: str | None = None

class EducationGenerateRequest(BaseModel):
    prompt: str
    module: str | None = None

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
# Helpers
# ---------------------------------------------------------------------------

def _url(path: str | None) -> str | None:
    if not path:
        return None
    return f"/download/{Path(path).name}"

def _save_history(prompt, mode, module, title, body, result):
    save_workspace_item({
        "prompt":   prompt,
        "mode":     mode,
        "module":   module,
        "title":    title,
        "preview":  body[:300],
        "pdf_url":  _url(result.get("pdf_path")),
        "docx_url": _url(result.get("docx_path")),
        "pptx_url": _url(result.get("pptx_path")),
        "xlsx_url": _url(result.get("xlsx_path")),
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# SPA
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, response_model=None, include_in_schema=False)
def home():
    index = _DIST_DIR / "index.html"
    if index.is_file():
        return FileResponse(str(index))
    return HTMLResponse("<h1>Frontend not built.</h1><p>Run: <code>cd frontend &amp;&amp; npm run build</code></p>", status_code=503)

@app.get("/health")
def health() -> dict:
    return {"status": "ok", "modules": list(_MODULE_NAMES.keys())}


# ---------------------------------------------------------------------------
# Main unified build endpoint — THE CENTRAL BRAIN
# ---------------------------------------------------------------------------

@app.post("/api/build")
def api_build(req: BuildRequest) -> dict:
    """Single entry-point. Auto-detects intent and routes to the correct AI module."""
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=422, detail="Prompt must not be empty.")
    try:
        raw = _brain.run(req.prompt.strip(), module_hint=req.module)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    module = raw.get("module", "document")
    _save_history(req.prompt, module, module, raw["title"], raw["body"], raw)
    return {
        "success":    True,
        "module":     module,
        "module_name":raw.get("module_name", _MODULE_NAMES.get(module, "Easy AI")),
        "title":      raw["title"],
        "body":       raw["body"],
        "sections":   raw["sections"],
        "pdf_url":    _url(raw.get("pdf_path")),
        "docx_url":   _url(raw.get("docx_path")),
        "pptx_url":   _url(raw.get("pptx_path")),
        "xlsx_url":   _url(raw.get("xlsx_path")),
        "meta": {
            "intent":    module,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        },
    }


# ---------------------------------------------------------------------------
# Module detection preview
# ---------------------------------------------------------------------------

@app.post("/api/detect-module")
def api_detect_module(req: SimpleGenerateRequest) -> dict:
    """Return which module would handle this prompt without generating content."""
    module = detect_module(req.prompt)
    return {"module": module, "module_name": _MODULE_NAMES.get(module, "Easy AI")}


# ---------------------------------------------------------------------------
# Legacy /generate endpoint (backwards compat)
# ---------------------------------------------------------------------------

@app.post("/generate")
async def generate(req: SimpleGenerateRequest) -> dict:
    try:
        result = _brain.run(req.prompt, doc_type="document")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")
    return {
        "content": result["body"],
        "pdf":  _url(result.get("pdf_path")),
        "docx": _url(result.get("docx_path")),
    }

@app.post("/generate-document", response_model=GenerateResponse)
def generate_document(req: GenerateRequest) -> GenerateResponse:
    try:
        result = _brain.run(req.prompt, doc_type=req.doc_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")
    _save_history(req.prompt, req.doc_type, result.get("module","document"), result["title"], result["body"], result)
    return GenerateResponse(
        title=result["title"], body=result["body"], sections=result["sections"],
        pdf_url=_url(result.get("pdf_path")), docx_url=_url(result.get("docx_path")),
        pptx_url=_url(result.get("pptx_path")), xlsx_url=_url(result.get("xlsx_path")),
    )


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

@app.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    import tempfile
    safe_name  = os.path.basename(filename)
    export_dir = os.path.realpath(os.path.join(tempfile.gettempdir(), "docgen_exports"))
    candidate  = os.path.join(export_dir, safe_name)
    resolved   = os.path.realpath(candidate)
    if not resolved.startswith(export_dir + os.sep):
        raise HTTPException(status_code=403, detail="Access denied.")
    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="File not found.")
    ext = Path(resolved).suffix.lower()
    return FileResponse(resolved, media_type=_MIME.get(ext, "application/octet-stream"), filename=safe_name)


# ---------------------------------------------------------------------------
# Workspace history
# ---------------------------------------------------------------------------

@app.get("/workspace/history")
def workspace_history() -> list:
    return list_workspace_items()

@app.delete("/workspace/clear")
def workspace_clear() -> dict:
    from workspace_store import clear_workspace
    try:
        clear_workspace()
    except Exception:
        pass
    return {"cleared": True}


# ---------------------------------------------------------------------------
# Templates library
# ---------------------------------------------------------------------------

@app.get("/api/templates")
def get_templates(module: str = "") -> list:
    """Return all templates, or filter by module."""
    if module:
        return [t for t in TEMPLATES if t["module"] == module]
    return TEMPLATES


# ---------------------------------------------------------------------------
# Module listing
# ---------------------------------------------------------------------------

@app.get("/api/modules")
def list_modules() -> list:
    """Return all available AI modules with metadata."""
    return [
        {"id": k, "name": v, "icon": _MODULE_ICON.get(k, "🤖")}
        for k, v in _MODULE_NAMES.items()
    ]

_MODULE_ICON = {
    "document":    "📄", "slides": "📽️", "excel": "📊",
    "professor":   "🎓", "teacher": "📚", "exam": "📝",
    "simulation":  "💼", "court": "⚖️", "student": "🙋",
    "admin":       "🗂️", "multilingual": "🌐", "integrity": "🛡️",
    "business":    "🏢", "research": "🔬", "analytics": "📈",
    "content":     "✍️", "course": "🏫", "upload": "📁",
}


# ---------------------------------------------------------------------------
# Education endpoints
# ---------------------------------------------------------------------------

@app.get("/education/modules")
def list_education_modules() -> list:
    return MODULE_INFO

@app.post("/education/generate", response_model=EducationGenerateResponse)
def education_generate(req: EducationGenerateRequest) -> EducationGenerateResponse:
    try:
        result = _edu.generate(req.prompt, module=req.module)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Education generation failed: {exc}")

    pdf_path  = export_pdf(result["title"], result["sections"])
    docx_path = export_docx(result["title"], result["sections"])
    save_workspace_item({
        "prompt": req.prompt, "mode": "education", "module": result["module"],
        "title": result["title"], "preview": result["body"][:300],
        "pdf_url": f"/download/{Path(pdf_path).name}",
        "docx_url": f"/download/{Path(docx_path).name}",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    })
    return EducationGenerateResponse(
        module=result["module"], title=result["title"], body=result["body"],
        sections=result["sections"],
        pdf_url=f"/download/{Path(pdf_path).name}",
        docx_url=f"/download/{Path(docx_path).name}",
    )

@app.post("/education/chat")
def education_chat(req: EducationChatRequest) -> dict:
    module = req.module or "student"
    add_chat_message(module, "user", req.message)
    try:
        response = _edu.chat(req.message, module=module)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}")
    reply = response.get("reply") or str(response)
    add_chat_message(module, "assistant", reply)
    return {"module": module, "reply": reply, "history": get_chat_history(module)}


# ---------------------------------------------------------------------------
# Upload AI — reads uploaded files and generates structured summaries
# ---------------------------------------------------------------------------

@app.post("/api/upload")
async def api_upload(
    file: UploadFile = File(...),
    module: str = Form(default="upload"),
) -> dict:
    """Upload any file → Upload AI extracts text → returns summary + key points + next steps."""
    try:
        raw_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read file: {exc}")

    filename = file.filename or "uploaded_file"
    text_content = _extract_text(raw_bytes, filename)

    # Persist the upload record
    save_uploaded_material(filename=filename, module=module, extracted_text=text_content)

    # Generate summary via Upload AI
    summary_result = _upload.summarise(text_content, filename=filename)

    # Also export to PDF + DOCX
    pdf_path  = export_pdf(summary_result["title"], summary_result["sections"])
    docx_path = export_docx(summary_result["title"], summary_result["sections"])

    _save_history(f"[Uploaded: {filename}]", "upload", "upload",
                  summary_result["title"], summary_result["body"],
                  {"pdf_path": pdf_path, "docx_path": docx_path})

    return {
        "success":    True,
        "filename":   filename,
        "module":     "upload",
        "module_name":"Upload AI",
        "title":      summary_result["title"],
        "body":       summary_result["body"],
        "sections":   summary_result["sections"],
        "keywords":   summary_result.get("keywords", []),
        "word_count": summary_result.get("word_count", 0),
        "pdf_url":    f"/download/{Path(pdf_path).name}",
        "docx_url":   f"/download/{Path(docx_path).name}",
    }


# Legacy upload endpoint (education context)
@app.post("/education/upload-material")
async def education_upload_material(
    file: UploadFile = File(...),
    module: str = "student",
) -> dict:
    try:
        raw = await file.read()
        text_content = _extract_text(raw, file.filename or "file")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read file: {exc}")
    save_uploaded_material(filename=file.filename or "unknown", module=module, extracted_text=text_content)
    combined_prompt = (
        f"Summarise and create a study guide for the following material "
        f"from '{file.filename}':\n\n{text_content[:4000]}"
    )
    try:
        result = _edu.generate(combined_prompt, module=module or "student")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {exc}")
    pdf_path  = export_pdf(result["title"], result["sections"])
    docx_path = export_docx(result["title"], result["sections"])
    return {
        "filename": file.filename, "saved": True,
        "module": result["module"], "title": result["title"],
        "body": result["body"], "sections": result["sections"],
        "pdf_url": f"/download/{Path(pdf_path).name}",
        "docx_url": f"/download/{Path(docx_path).name}",
    }

@app.get("/education/materials")
def list_materials() -> list:
    return list_uploaded_materials()


# ---------------------------------------------------------------------------
# Text extraction helper
# ---------------------------------------------------------------------------

def _extract_text(raw_bytes: bytes, filename: str) -> str:
    """Extract plain text from uploaded file bytes based on extension."""
    fname = (filename or "").lower()

    # Plain text / markdown / csv / json
    if any(fname.endswith(ext) for ext in (".txt", ".md", ".csv", ".json", ".xml", ".html")):
        return raw_bytes.decode("utf-8", errors="replace")

    # PDF — try PyPDF2
    if fname.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
            return "\n".join(
                (page.extract_text() or "") for page in reader.pages
            )
        except Exception:
            return raw_bytes.decode("utf-8", errors="replace")

    # DOCX — try python-docx
    if fname.endswith(".docx"):
        try:
            from docx import Document as DocxDoc
            doc = DocxDoc(io.BytesIO(raw_bytes))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception:
            return raw_bytes.decode("utf-8", errors="replace")

    # XLSX — try openpyxl
    if fname.endswith((".xlsx", ".xls")):
        try:
            from openpyxl import load_workbook
            wb = load_workbook(io.BytesIO(raw_bytes), read_only=True, data_only=True)
            lines = []
            for ws in wb.worksheets:
                for row in ws.iter_rows(values_only=True):
                    line = " | ".join(str(c) for c in row if c is not None)
                    if line.strip():
                        lines.append(line)
            return "\n".join(lines)
        except Exception:
            return raw_bytes.decode("utf-8", errors="replace")

    # Fallback: decode as UTF-8
    return raw_bytes.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# SPA catch-all (must be last)
# ---------------------------------------------------------------------------

@app.get("/{full_path:path}", response_class=HTMLResponse, response_model=None, include_in_schema=False)
def serve_spa(full_path: str):
    if _DIST_DIR.is_dir():
        candidate = _DIST_DIR / full_path
        if candidate.is_file():
            return FileResponse(str(candidate))
        index = _DIST_DIR / "index.html"
        if index.is_file():
            return FileResponse(str(index))
    return HTMLResponse("<h1>Frontend not built.</h1>", status_code=503)
