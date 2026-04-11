# AGENTS.md

## Cursor Cloud specific instructions

### Overview
EASY AI DOC & EDUCATION CORE is a Flask + SocketIO monolith that generates professional documents (PDF, DOCX, XLSX, PPTX) and provides an education platform with 20 AI professors. All served from `app.py`.

### Running the app
```
PORT=8080 python3 app.py
```
- **Do NOT use port 5000** — Chrome blocks it. Use `8080`.
- The `PORT` env var controls the port (defaults to `8080`).
- No external database needed — SQLite auto-created if used.
- Generated files are stored in `/workspace/downloads/`.

### Project structure
- `app.py` — main Flask app with all routes
- `engines/master_brain.py` — intent detection and routing
- `engines/document_engine.py` — PDF/DOCX generation (ReportLab + python-docx)
- `engines/excel_engine.py` — XLSX generation (openpyxl)
- `engines/presentation_engine.py` — PPTX generation (python-pptx)
- `engines/education_engine.py` — 20 AI professors, course/syllabus/exam generation
- `templates/index.html` — frontend SPA
- `static/css/style.css` + `static/js/app.js` — frontend assets

### Key API endpoints
- `GET /api/health` — health check
- `POST /api/generate` — generate a specific file type (`{prompt, type, mode}`)
- `POST /api/smart-generate` — auto-detect intent and generate appropriate files
- `GET /api/professors` — list all 20 professors
- `POST /api/education/generate` — generate full course (`{professor, topic}`)
- `GET /api/files` — list generated files
- `GET /download/<filename>` — download a file

### No lint/test tooling
The repository does not include a linter config or automated test suite. Manual testing via browser and curl.
