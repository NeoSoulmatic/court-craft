#!/usr/bin/env bash
# One-time data + model setup inside the running API container.
set -euo pipefail

echo "==> Backfill (games, players, draft) — may take several minutes..."
docker compose --profile full exec api python -m app.ingest.run_backfill

echo "==> Phase 2b transactions..."
docker compose --profile full exec api python -m app.ingest.run_phase2b

echo "==> Phase 3 ML train + backtest..."
docker compose --profile full exec api python /app/ml/run_phase3.py

echo "==> Done. Open http://localhost:8080"
