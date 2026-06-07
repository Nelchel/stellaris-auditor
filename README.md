# Stellaris Auditor

Upload a Stellaris `.sav` file and get a strategic audit of your empire.

Stellaris Auditor analyzes your save and produces:
- empire scoring
- economic intelligence
- planet intelligence
- campaign narrative
- visual analytics
- history analytics
- save-to-save comparison

![Status](https://img.shields.io/badge/status-experimental-purple)
![Frontend](https://img.shields.io/badge/frontend-React-blue)
![Backend](https://img.shields.io/badge/backend-FastAPI-green)

## Demo on GitHub Pages

GitHub Pages hosts the React frontend only.

Because GitHub Pages cannot run FastAPI, the deployed page runs in demo mode with a sample report.

## Local full app

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend docs:

```txt
http://127.0.0.1:8000/docs
```

### Frontend

Install Node.js LTS first.

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```txt
http://127.0.0.1:5173
```

## GitHub Pages setup

1. Create a GitHub repo.
2. Push this project to `main`.
3. Go to **Settings → Pages**.
4. Source: **GitHub Actions**.
5. The workflow `.github/workflows/pages.yml` deploys automatically.

## Project structure

```txt
backend/
  app/
    main.py
    stellaris_auditor_core.py
    services/
      audit_service.py
      storage_service.py
      report_service.py
      planet_enrichment_service.py
      planet_intelligence_service.py
      evolution_service.py
      narrative_service.py
      visual_service.py
      history_service.py

frontend/
  src/
    components/
    lib/
    demo/
```

## Current limitations

- GitHub Pages demo mode uses sample data.
- Full `.sav` parsing requires running the FastAPI backend locally.
- Stellaris save parsing is experimental and may vary depending on game version/mods.

## Roadmap

- report browser
- drag & drop uploads
- packaged desktop app
- better planet name resolution
- export HTML/PDF reports
- hosted backend option


## V3.5.1

- Fixed dark/black Chart.js datasets on dark theme.
- Added explicit bright chart palette.
- Improved chart backgrounds, hover states and visual contrast.
- Removed GitHub Actions npm cache dependency on missing `package-lock.json`.


## V3.5.2

- Fixed History Analytics in GitHub Pages demo mode.
- Added bright chart palette to History graphs.
- Added error state for unavailable local `/history` API.
