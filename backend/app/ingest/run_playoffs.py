#!/usr/bin/env python3
"""Ingest playoff results + upcoming schedule for configured seasons.

Usage:
    cd backend && .venv/bin/python -m app.ingest.run_playoffs
"""

import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.database import Base
import app.models  # noqa: F401
from app.ingest.playoffs import ingest_all_playoffs


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Playoff ingest — seasons: {settings.seasons_list}")
    try:
        total = ingest_all_playoffs(session, settings.seasons_list)
        print(f"Done. {total} playoff rows processed.")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
