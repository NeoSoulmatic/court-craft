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
make backfill
# or: cd backend && .venv/bin/python -m app.ingest.run_backfill
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

## Phase 2b ingest (transactions)

```bash
make phase2b
```

Scrapes Basketball Reference season transaction pages (~3 requests, one per configured season).

## Phase 3 (ML pipeline)

Train XGBoost score models, backtest on **2025-26** holdout, wire predictions to the API:

```bash
make phase3
```

Requires Postgres populated (`make backfill`). Downloads free historical odds automatically. See `ml/odds/README.md` for the odds data source.

### Playoff predictions (demo)

The model is trained on **regular season only**. Playoff projections use the same model for showcase purposes:

```bash
make playoffs   # ingest playoff results + schedule, refresh predictions
```

Upcoming Finals games appear on the dashboard with a **Playoffs** badge and an experimental disclaimer.

## Phase 4 (live odds + market comparison)

Compare model projections to live market lines with implied win % and quarter-Kelly hints.

### 1. Get an Odds API key

1. Sign up at [the-odds-api.com](https://the-odds-api.com/) (free tier: **500 requests/month**).
2. Add to `.env`:

```env
ODDS_API_KEY=your_key_here
```

### 2. Daily refresh

```bash
make daily   # re-ingest current season, fetch odds, refresh predictions
```

Odds are cached for 6 hours (`ODDS_CACHE_HOURS`) so normal dashboard loads do not burn API quota.

### API

- `GET /api/v1/predictions/upcoming` — model + market enrichment
- `GET /api/v1/odds/status` — cache age and remaining monthly requests

## Roadmap

- [x] **Phase 1** — Monorepo scaffold, DB schema, ETL skeleton, API, UI shell
- [x] **Phase 2** — Player rosters + draft history ingest
- [x] **Phase 2b** — Transaction timeline
- [x] **Phase 3** — Feature pipeline, model training, backtest page
- [x] **Phase 4** — Live odds, model vs market, Kelly hints, daily job
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
| Draft history | `nba_api` DraftHistory |
| Transactions | Basketball Reference season pages |
| Historical odds | Kaggle closing-lines datasets (Phase 3) |
| Live odds | The Odds API free tier — 500 req/month (Phase 4) |

## Disclaimer

Predictions are for education and portfolio demonstration only. Not betting advice.
