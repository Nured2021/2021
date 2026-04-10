# ODEX

ODEX is an AI-powered application builder. Users enter a natural-language prompt describing what they want to build, and ODEX orchestrates a multi-stage pipeline (Plan → Build → Fix → Test) that runs against a backend engine, streams live logs, and renders a live preview of the generated application.

## Repository Structure

```
.
├── engine/            # Python backend – AI build engines and API server
├── ui/
│   └── dashboard/     # React (Vite) front-end dashboard
│       ├── components/    # BuilderCore, Sidebar, PreviewPanel, ConsolePanel, …
│       ├── BuilderWorkspace.jsx  # Main workspace – orchestrates the build flow
│       ├── api.js         # API client helpers
│       └── vite.config.js
├── package.json       # Root Node.js manifest (odex v1.0.0)
└── ODEX_Full_Engineering_Blueprint.pdf  # Full system design document
```

## How It Works

1. The user types a prompt in the **Builder Workspace** and clicks **Start**.
2. The UI posts `{ "prompt": "<user input>" }` to `POST /build` on the backend.
3. The backend runs the AI pipeline and returns:
   - `steps` – ordered build stages shown in the center panel (Plan / Build / Fix / Test)
   - `logs` – streaming log messages rendered in the console panel
   - `preview_url` – URL of the live preview loaded in the iframe
4. The left **Sidebar** shows available AI engines loaded from `GET /api/engines`.
5. A health check (`GET /api/health`) is performed on startup; a banner is shown if the backend is unreachable.

## Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- Backend server running on `http://localhost:8080`

### Frontend (UI)

```bash
cd ui/dashboard
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173` by default.

### Backend (Engine)

Start the Python backend so it listens on port 8080. Refer to the `engine/` directory and `ODEX_Full_Engineering_Blueprint.pdf` for full setup instructions.

## API Endpoints

| Method | Path           | Description                              |
|--------|----------------|------------------------------------------|
| GET    | /api/health    | Health check                             |
| GET    | /api/engines   | List available AI engines and their status |
| POST   | /build         | Start a build with `{ "prompt": "…" }`   |

## Contributing

1. Fork the repository and create a feature branch.
2. Open a pull request with a clear description of your changes.
3. Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) issue template for new ideas.
