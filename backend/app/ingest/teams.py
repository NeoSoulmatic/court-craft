"""Ingest NBA teams from nba_api."""

import time

from nba_api.stats.static import teams as nba_teams
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team


def ingest_teams(session: Session) -> int:
    rows = nba_teams.get_teams()
    count = 0
    for row in rows:
        existing = session.get(Team, row["id"])
        if existing:
            existing.abbreviation = row["abbreviation"]
            existing.full_name = row["full_name"]
            existing.city = row["city"]
            existing.nickname = row["nickname"]
        else:
            session.add(
                Team(
                    id=row["id"],
                    abbreviation=row["abbreviation"],
                    full_name=row["full_name"],
                    city=row["city"],
                    nickname=row["nickname"],
                )
            )
        count += 1
    session.commit()
    return count


def ensure_teams(session: Session) -> None:
    result = session.execute(select(Team.id).limit(1)).scalar_one_or_none()
    if result is None:
        ingest_teams(session)
        time.sleep(0.6)
