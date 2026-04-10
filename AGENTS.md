# AGENTS.md

## Cursor Cloud specific instructions

### Architecture

Easy AI is a full-stack AI workspace app with 18 AI modules. Code lives on the `copilot/add-main-ai-system` branch (the `main` branch is empty).

| Layer | Tech | Port | Entrypoint |
|-------|------|------|------------|
| Backend | FastAPI + Uvicorn (Python) | 8000 | `backend/main.py` |
| Frontend | React 19 + Vite 8 | 5173 | `frontend/src/main.jsx` → `App.jsx` |
| Database | SQLite (auto-created) | — | `backend/easy_ai.db` |

### Running services

- **Backend**: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
- **Frontend**: `cd frontend && npm run dev`
- The Vite config (`frontend/vite.config.js`) proxies `/api`, `/generate`, `/education`, `/workspace`, `/download`, `/health` to `http://localhost:8000`, so the frontend at `:5173` talks to the backend without CORS issues.

### Gotchas

- The `main` branch has no code. Always work from `copilot/add-main-ai-system` or a branch based on it.
- `frontend/.env` must exist (copy from `.env.example`): `VITE_API_URL=http://localhost:8000`.
- The `NewDashboard` overlay (`showNewDashboard` state in `App.jsx`) was previously defaulting to `true`, hiding the real 3-panel layout. It is now `false` so the Sidebar + PromptPanel + PreviewPanel renders on load.
- No external database or Docker is needed — SQLite is embedded and auto-created on first backend startup.
- Pre-existing ESLint errors exist (28 errors, 5 warnings) — all in existing code, not introduced by setup. Most are `react-hooks` rule violations.

### Lint / Test / Build

- **Lint**: `cd frontend && npx eslint .`
- **Build**: `cd frontend && npm run build` (outputs to `frontend/dist/`)
- No automated test suite exists in this repo.
