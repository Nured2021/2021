# DocGen AI

A full-stack document generation web application.

## Architecture

```
├── backend/          # Python FastAPI server
│   ├── main.py           # FastAPI app + /generate-document endpoint
│   ├── main_ai.py        # Main AI controller
│   ├── document_ai.py    # Document AI (content generation)
│   ├── export_utils.py   # PDF & DOCX export
│   └── requirements.txt
└── frontend/         # React + Vite dashboard
    └── src/
        ├── App.jsx
        ├── api/documentApi.js
        └── components/
            ├── Sidebar.jsx         # Left navigation
            ├── PromptPanel.jsx     # Center prompt input
            └── PreviewPanel.jsx    # Right live preview
```

## Getting Started

### Single-Server (Integrated UI + API)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000` — the backend serves both the dashboard UI and the API.

### Frontend (React – optional)

The React app in `frontend/` provides an alternative UI with richer interactivity.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

React app available at `http://localhost:5173` (requires backend running on port 8000).

## Usage

1. Open `http://localhost:8000`
2. Enter your prompt in the text box
3. Click **Generate**
4. Preview the generated content
5. Download as **PDF** or **Word (.docx)**

## API

### `POST /generate`

Simple endpoint used by the integrated HTML dashboard.

```json
{ "prompt": "Write a project proposal for a mobile app" }
```

Response:

```json
{
  "content": "...",
  "pdf": "/download/<uuid>.pdf",
  "docx": "/download/<uuid>.docx"
}
```

### `POST /generate-document`

Full endpoint with doc-type selection (used by the React frontend).

```json
{
  "prompt": "Write a project proposal for a mobile app",
  "doc_type": "document"
}
```

Response includes `title`, `body`, `sections`, `pdf_url`, `docx_url`.
