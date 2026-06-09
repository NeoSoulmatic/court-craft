#!/usr/bin/env python3
"""Daily refresh: current-season games, live odds, predictions.

Usage (from repo root):
    make daily
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.ingest.games import ingest_season_games
from app.services.odds import fetch_live_odds

REPO_ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    Session = sessionmaker(bind=engine)
    session = Session()

    current_season = settings.seasons_list[-1]
    print(f"Court Craft daily — refreshing {current_season} regular season games...")
    try:
        count = ingest_season_games(session, current_season, season_type="Regular Season")
        session.commit()
        print(f"  {count} games upserted")
    except Exception as exc:
        session.rollback()
        print(f"  ERROR ingesting games: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()

    time.sleep(0.5)

    print("Fetching live odds...")
    snapshot = fetch_live_odds(force=True)
    if snapshot.get("error"):
        print(f"  Odds note: {snapshot['error']}")
    else:
        remaining = snapshot.get("requests_remaining")
        msg = f"  {len(snapshot.get('events', []))} events cached"
        if remaining is not None:
            msg += f" ({remaining} API requests remaining this month)"
        print(msg)

    print("Refreshing predictions...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    predict_script = REPO_ROOT / "ml" / "predict.py"
    result = subprocess.run(
        [sys.executable, str(predict_script)],
        cwd=str(REPO_ROOT / "backend"),
        env=env,
        check=False,
    )
    if result.returncode != 0:
        print("  ERROR running predict.py", file=sys.stderr)
        return result.returncode

    print("Daily refresh complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
