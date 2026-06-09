# Court Craft

Full-stack NBA analytics and machine learning platform — player stats, team performance, draft data, roster moves, and game predictions (moneyline, spread, total).

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Vite, React, TypeScript, Tailwind, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| ML | scikit-learn, XGBoost |
| Data | `nba_api` (3 seasons to start, expandable) |

## Quick start (local)

### 1. Database

```bash
docker compose up -d
```

Postgres runs on **localhost:5433** (avoids conflict with default 5432).

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

### 3. Data backfill (3 seasons)

```bash
cd backend
source .venv/bin/activate
python -m app.ingest.run_backfill
```

Takes a few minutes — `nba_api` rate-limits requests.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Project structure

```
court-craft/
├── frontend/          # React + TypeScript dashboard
├── backend/           # FastAPI + ETL
├── ml/                # Feature engineering, training, backtest
├── data/              # Local data (gitignored)
└── docker-compose.yml
```

## Phase 2 ingest (players + draft)

After Phase 1 backfill, load rosters and draft history:

```bash
make phase2
```

Takes ~1–2 minutes (30 roster API calls + draft history).

## Roadmap

- [x] **Phase 1** — Monorepo scaffold, DB schema, ETL skeleton, API, UI shell
- [x] **Phase 2** — Player rosters + draft history ingest
- [ ] **Phase 2b** — Transaction timeline
- [ ] **Phase 3** — Feature pipeline, model training, backtest page
- [ ] **Phase 4** — Live predictions on dashboard
- [ ] **Phase 5** — Docker all-in-one, deploy demo, README polish

## Expanding beyond 3 seasons

Edit `SEASONS_BACKFILL` in `.env`:

```env
SEASONS_BACKFILL=2018-19,2019-20,2020-21,2021-22,2022-23,2023-24,2024-25
```

Re-run the backfill script. No schema changes needed.

## Data sources (free tier)

| Data | Source |
|------|--------|
| Games, box scores | `nba_api` |
| Draft history | Kaggle / BBRef CSV (Phase 2) |
| Historical odds | Kaggle closing-lines datasets (Phase 3) |
| Live odds | The Odds API free tier — 500 req/month (Phase 4) |

## Disclaimer

Predictions are for education and portfolio demonstration only. Not betting advice.
