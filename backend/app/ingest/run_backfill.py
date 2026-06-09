#!/usr/bin/env python3
"""Run initial data backfill for configured seasons.

Usage (from repo root):
    cd backend && python -m app.ingest.run_backfill
"""

import sys
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.ingest.games import ingest_season_games
from app.ingest.teams import ingest_teams


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Court Craft backfill — seasons: {settings.seasons_list}")
    print("Ingesting teams...")
    team_count = ingest_teams(session)
    print(f"  {team_count} teams upserted")

    total_games = 0
    for season in settings.seasons_list:
        print(f"Ingesting games for {season}...")
        try:
            count = ingest_season_games(session, season)
            total_games += count
            print(f"  {count} games upserted")
        except Exception as exc:
            print(f"  ERROR for {season}: {exc}", file=sys.stderr)
        time.sleep(1.0)

    print(f"Done. Total new games: {total_games}")
    session.close()


if __name__ == "__main__":
    main()
