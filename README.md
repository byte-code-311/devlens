# DevLens

DevLens helps developers turn bug reports into evidence-backed triage notes. It searches a small bundled sample codebase and related issues, then presents possible leads and test ideas with links to the material behind them.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer

## First-time setup

From the DevLens project folder, open two PowerShell terminals.

In terminal 1, install and seed the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`; its health endpoint is `http://127.0.0.1:8000/api/health`.
The default SQLite database is created at `backend/devlens.db` the first time the API is used.

In terminal 2, start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. The frontend proxies `/api` requests to the backend.

## Optional AI mode

DevLens works without an API key in deterministic baseline mode. To enable AI-assisted triage, copy `.env.example` to `.env` in the DevLens project folder and set `OPENAI_API_KEY`. `OPENAI_MODEL` can select a model available to your account. Restart the backend after changing `.env`. The key stays in the backend environment and is never sent to the browser.

## Checks

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests -q
cd ..\frontend
npm test -- --run
npm run build
```

## Project scope

The local MVP includes report entry and history, a curated educational corpus, lexical evidence retrieval, baseline and optional structured AI triage, source citations, and user feedback. It does not connect to a live GitHub/GitLab repository, clone private code, or execute code. Suggestions are investigative aids, not confirmed diagnoses.

See `docs/project/abstract.md`, `docs/project/architecture.md`, and `docs/project/demo-script.md` for final-year project material and presentation guidance.
