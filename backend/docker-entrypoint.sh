#!/bin/sh
set -e

python <<'PY'
import os
import sys
import time

import psycopg2

url = os.environ.get("DATABASE_URL_SYNC") or os.environ.get("DATABASE_URL", "")
if not url:
    sys.exit(0)

sync = url.replace("postgresql+asyncpg://", "postgresql://", 1).replace(
    "postgres://", "postgresql://", 1
)

for attempt in range(30):
    try:
        psycopg2.connect(sync)
        print("Database is ready.")
        break
    except psycopg2.OperationalError:
        print(f"Waiting for database ({attempt + 1}/30)...")
        time.sleep(2)
else:
    print("Database not reachable after 60s", file=sys.stderr)
    sys.exit(1)
PY

PORT="${PORT:-${APP_PORT:-8000}}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
