"""Ingest NBA draft history from nba_api."""

import time

from nba_api.stats.endpoints import drafthistory
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.draft import DraftPick


def ingest_draft_history(session: Session) -> int:
    """Upsert all draft picks from NBA DraftHistory endpoint."""
    endpoint = drafthistory.DraftHistory()
    df = endpoint.get_data_frames()[0]
    time.sleep(0.6)

    count = 0
    for _, row in df.iterrows():
        season = str(int(row["SEASON"]))
        pick_overall = int(row["OVERALL_PICK"])
        player_id = int(row["PERSON_ID"]) if row["PERSON_ID"] == row["PERSON_ID"] else None
        team_id = int(row["TEAM_ID"]) if row["TEAM_ID"] == row["TEAM_ID"] else None

        college = None
        org_type = str(row["ORGANIZATION_TYPE"]) if row["ORGANIZATION_TYPE"] == row["ORGANIZATION_TYPE"] else ""
        org = str(row["ORGANIZATION"]) if row["ORGANIZATION"] == row["ORGANIZATION"] else None
        if org and "college" in org_type.lower():
            college = org

        existing = session.execute(
            select(DraftPick).where(
                DraftPick.season == season,
                DraftPick.pick_overall == pick_overall,
            )
        ).scalar_one_or_none()

        pick = existing or DraftPick(season=season, pick_overall=pick_overall)
        pick.round = int(row["ROUND_NUMBER"])
        pick.team_id = team_id
        pick.player_id = player_id
        pick.player_name = str(row["PLAYER_NAME"])
        pick.college = college

        if not existing:
            session.add(pick)
        count += 1

    session.commit()
    return count
