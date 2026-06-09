"""Ingest NBA draft history from nba_api."""

import time

from nba_api.stats.endpoints import drafthistory
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.draft import DraftPick
from app.models.player import Player
from app.models.team import Team


def _resolve_team_id(session: Session, team_id: int | None) -> int | None:
    if team_id is None:
        return None
    with session.no_autoflush:
        return team_id if session.get(Team, team_id) else None


def _resolve_player_id(session: Session, player_id: int | None, player_name: str) -> int | None:
    if player_id is None:
        return None
    with session.no_autoflush:
        if session.get(Player, player_id):
            return player_id
    session.add(Player(id=player_id, full_name=player_name, is_active=False))
    session.flush()
    return player_id


def ingest_draft_history(session: Session) -> int:
    """Upsert all draft picks from NBA DraftHistory endpoint."""
    endpoint = drafthistory.DraftHistory()
    df = endpoint.get_data_frames()[0]
    time.sleep(0.6)

    count = 0
    for _, row in df.iterrows():
        draft_type = str(row["DRAFT_TYPE"]) if row["DRAFT_TYPE"] == row["DRAFT_TYPE"] else ""
        if draft_type != "Draft":
            continue

        season = str(int(row["SEASON"]))
        pick_overall = int(row["OVERALL_PICK"])
        raw_player_id = int(row["PERSON_ID"]) if row["PERSON_ID"] == row["PERSON_ID"] else None
        raw_team_id = int(row["TEAM_ID"]) if row["TEAM_ID"] == row["TEAM_ID"] else None

        college = None
        org_type = str(row["ORGANIZATION_TYPE"]) if row["ORGANIZATION_TYPE"] == row["ORGANIZATION_TYPE"] else ""
        org = str(row["ORGANIZATION"]) if row["ORGANIZATION"] == row["ORGANIZATION"] else None
        if org and "college" in org_type.lower():
            college = org

        player_name = str(row["PLAYER_NAME"])
        team_id = _resolve_team_id(session, raw_team_id)
        player_id = _resolve_player_id(session, raw_player_id, player_name)

        with session.no_autoflush:
            existing = session.execute(
                select(DraftPick).where(
                    DraftPick.season == season,
                    DraftPick.pick_overall == pick_overall,
                )
            ).scalars().first()

        pick = existing or DraftPick(season=season, pick_overall=pick_overall)
        pick.round = int(row["ROUND_NUMBER"])
        pick.team_id = team_id
        pick.player_id = player_id
        pick.player_name = player_name
        pick.college = college

        if not existing:
            session.add(pick)
        count += 1

    session.commit()
    return count
