#!/usr/bin/env python3
"""Run Phase 2b ingest — transaction timeline from Basketball Reference.

Usage:
    cd backend && .venv/bin/python -m app.ingest.run_phase2b
"""

import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import Base
import app.models  # noqa: F401
from app.ingest.transactions import ingest_transactions


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Phase 2b ingest — transactions for seasons: {settings.seasons_list}")
    try:
        count = ingest_transactions(session, settings.seasons_list)
        print(f"  {count} new transactions ingested")
    except Exception as exc:
        print(f"  ERROR: {exc}", file=sys.stderr)
        raise

    print("Phase 2b complete.")
    session.close()


if __name__ == "__main__":
    main()
