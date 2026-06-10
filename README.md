# Court Craft

Full-stack NBA analytics and machine learning platform — player stats, team performance, draft data, roster moves, and game predictions (moneyline, spread, total) with live market comparison.

[![Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

## Features

- **Analytics** — teams, players, games, draft history, transaction timeline
- **ML predictions** — XGBoost score models, moneyline / spread / total projections
- **Backtest dashboard** — 2025-26 holdout metrics vs closing lines
- **Live odds** — model vs market with implied win % and quarter-Kelly hints (The Odds API)

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Vite, React, TypeScript, Tailwind, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| ML | scikit-learn, XGBoost |
| Data | `nba_api`, Basketball Reference, historical + live odds |

## Quick start (local dev)

### 1. Database

```bash
make db
```

Postgres on **localhost:5433**.

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Data + ML

```bash
make backfill    # games, players, draft (~few min)
make phase2b     # transactions
make phase3      # train models + backtest
```

Optional: `make daily` for current-season refresh + live odds (requires `ODDS_API_KEY`).

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

---

## Docker (all-in-one)

Run the full stack — Postgres, API, and nginx frontend — with one command:

```bash
cp .env.example .env   # add ODDS_API_KEY if you have one
make stack             # docker compose --profile full up --build -d
```

| Service | URL |
|---------|-----|
| **App (UI)** | http://localhost:8080 |
| **API** | http://localhost:8000 |
| **Postgres** | localhost:5433 |

### First-time data load (inside Docker)

After `make stack`, populate the database and train models:

```bash
./scripts/docker-bootstrap.sh
```

This runs backfill, transactions, and Phase 3 training inside the API container (~10–15 minutes).

Logs: `make stack-logs` · Stop: `make down`

> **Note:** Run `make phase3` locally before `make stack` if you want ML artifacts baked into the API image. Otherwise bootstrap trains inside the container.

---

## Deploy (Render)

A [Render Blueprint](https://render.com/docs/blueprint-spec) is included for a free-tier demo.

1. Push this repo to GitHub.
2. In Render → **New** → **Blueprint** → connect the repo.
3. Set `ODDS_API_KEY` in the web service environment (optional).
4. After deploy, open the Render **Shell** on the web service and run:

```bash
python -m app.ingest.run_backfill
python -m app.ingest.run_phase2b
python /app/ml/run_phase3.py
```

The all-in-one `Dockerfile` serves the React UI and API on the same URL (`SERVE_STATIC=1`).

Update `CORS_ORIGINS` in `render.yaml` to match your Render hostname after the first deploy.

---

## Project structure

```
court-craft/
├── frontend/          # React dashboard (nginx in Docker)
├── backend/           # FastAPI + ETL
├── ml/                # Features, training, backtest, live odds math
├── scripts/           # Docker bootstrap helpers
├── Dockerfile         # All-in-one image (Render)
├── docker-compose.yml # db + api + web (profile: full)
└── render.yaml        # Render Blueprint
```

## API highlights

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | Status + configured seasons |
| `GET /api/v1/predictions/upcoming` | Model + live market enrichment |
| `GET /api/v1/odds/status` | Odds cache + API quota |
| `GET /api/v1/model/backtest` | Holdout backtest metrics |

## Makefile targets

| Target | Description |
|--------|-------------|
| `make db` | Start Postgres only |
| `make stack` | Full Docker stack (UI + API + DB) |
| `make backfill` | Ingest games, players, draft |
| `make phase2b` | Transaction timeline |
| `make phase3` | ML train + backtest + predict |
| `make daily` | Refresh season, odds, predictions |
| `make playoffs` | Playoff ingest + predictions (demo) |

## Live odds (Phase 4)

1. Sign up at [the-odds-api.com](https://the-odds-api.com/) (free: 500 req/month).
2. Add to `.env`: `ODDS_API_KEY=your_key_here`
3. Run `make daily` — odds cached 6h by default.

## Expanding seasons

Edit `SEASONS_BACKFILL` in `.env` and re-run `make backfill`.

## Data sources

| Data | Source |
|------|--------|
| Games, box scores | `nba_api` |
| Draft history | `nba_api` DraftHistory |
| Transactions | Basketball Reference |
| Historical odds | kyleskom OddsData.sqlite (Phase 3) |
| Live odds | The Odds API (Phase 4) |

## CI/CD (GitHub Actions)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** | Push / PR to `main` | Pytest, frontend lint + build, Docker image builds |
| **Deploy** | After CI succeeds on `main` | POST to Render deploy hook (optional) |
| **Daily refresh** | Cron + manual | Production `make daily` via GitHub secrets |

### Repo secrets (optional)

| Secret | Used by |
|--------|---------|
| `RENDER_DEPLOY_HOOK_URL` | Deploy — from Render → Service → Settings → Deploy Hook |
| `DATABASE_URL` | Daily — Render Postgres **Internal** URL (`postgres://...`) |
| `ODDS_API_KEY` | Daily — live odds fetch |

If Render is already connected to GitHub, pushes to `main` auto-deploy; the deploy hook is a backup.

Local tests: `pip install -r requirements-dev.txt && pytest`

---

## Roadmap

- [x] Phase 1 — Scaffold, DB, ETL, API, UI
- [x] Phase 2 — Players + draft
- [x] Phase 2b — Transactions
- [x] Phase 3 — ML pipeline + backtest page
- [x] Phase 4 — Live odds + Kelly hints
- [x] Phase 5 — Docker all-in-one + Render deploy

## Disclaimer

Predictions are for education and portfolio demonstration only. Not betting advice.
