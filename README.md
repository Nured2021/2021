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

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API available at `http://localhost:8000`

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App available at `http://localhost:5173`

## Usage

1. Select a document type from the left sidebar (Documents, Excel, Presentation)
2. Enter your prompt in the center input box
3. Click **Generate**
4. Preview the result on the right panel
5. Download as **PDF** or **Word (.docx)**

## API

### `POST /generate-document`

```json
{
  "prompt": "Write a project proposal for a mobile app",
  "doc_type": "document"
}
```

Response includes `title`, `body`, `sections`, `pdf_url`, `docx_url`.
