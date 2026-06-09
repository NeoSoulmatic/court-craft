# Court Craft ML Pipeline

## Overview

Score-based prediction pipeline. One model predicts home/away points; markets are derived:

- **Moneyline** — P(home wins) from predicted margin distribution
- **Spread** — predicted margin vs market line
- **Total** — predicted combined score vs O/U line

## Scripts (coming in Phase 3)

| Script | Purpose |
|--------|---------|
| `features/build.py` | Rolling team stats, rest days, Elo |
| `train.py` | Train XGBoost regressors on historical games |
| `backtest.py` | Evaluate vs closing lines (historical CSV) |
| `predict.py` | Score upcoming games, write to DB or JSON |

## Data expansion

Start with 3 seasons (`SEASONS_BACKFILL` in `.env`). To expand:

1. Add seasons to `SEASONS_BACKFILL` (e.g. `2015-16,...,2024-25`)
2. Re-run `python -m app.ingest.run_backfill`
3. Re-run feature build + train

## Historical odds (free)

For spread/total backtesting, ingest a Kaggle closing-lines dataset into `data/odds/`.
See root README for sources.
