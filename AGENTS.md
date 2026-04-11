# AGENTS.md

## Cursor Cloud specific instructions

### Overview
ORD AI Platform is a Flask + SocketIO monolith serving both the API and frontend from a single `app.py`. It uses SQLite (auto-created, zero-config) and has no external service dependencies.

### Running the app
```
PORT=8080 python3 app.py
```
- **Do NOT use port 5000** — Chrome blocks it (reserved for AirPlay/other services). Use `8080` or any other unreserved port.
- The app reads the `PORT` env var (defaults to `5000` if unset).
- All 14 protection systems and the engine layer load automatically on startup.
- No database setup is needed — SQLite DBs are auto-created in `/tmp/`.

### Dependencies
- `pip install -r requirements.txt` — only 4 required packages (flask, flask-socketio, eventlet, gunicorn). All other deps in the file are commented out as optional.
- Python 3.12+ is available in the environment.

### No lint/test tooling
- The repository does not include a linter config, test framework, or automated test suite.
- Manual testing is done via the browser UI and API endpoints (`/api/state`, `/api/ai_chat`, `/api/build`, etc.).

### Key API endpoints
See `README.md` for the full list. Core ones: `GET /api/state`, `POST /api/build`, `POST /api/ai_chat`, `GET /api/protection/status`.
