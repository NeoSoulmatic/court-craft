#!/usr/bin/env python3
"""Run Phase 2 ingest only (players + draft) without re-fetching games.

Usage:
    cd backend && python -m app.ingest.run_phase2
"""

import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import Base
import app.models  # noqa: F401
from app.ingest.draft import ingest_draft_history
from app.ingest.players import ingest_players


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Phase 2 ingest — players + draft")
    try:
        static_count, roster_count = ingest_players(session, season=settings.seasons_list[-1])
        print(f"  {static_count} players in index, {roster_count} roster rows updated")
    except Exception as exc:
        print(f"  ERROR ingesting players: {exc}", file=sys.stderr)
        raise

    try:
        draft_count = ingest_draft_history(session)
        print(f"  {draft_count} draft picks upserted")
    except Exception as exc:
        print(f"  ERROR ingesting draft: {exc}", file=sys.stderr)
        raise

    print("Phase 2 complete.")
    session.close()


if __name__ == "__main__":
    main()
