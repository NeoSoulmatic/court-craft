"""Ingest NBA players from nba_api static data and team rosters."""

import time
from datetime import datetime

from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import players as nba_players
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team


def _parse_birth_date(value: str | None):
    if not value or value != value:  # NaN check
        return None
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_weight(value) -> int | None:
    if value is None or value != value:
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def ingest_players_static(session: Session) -> int:
    """Upsert all players from nba_api static index (no extra API calls)."""
    count = 0
    for row in nba_players.get_players():
        player = session.get(Player, row["id"])
        if player:
            player.full_name = row["full_name"]
            player.first_name = row.get("first_name")
            player.last_name = row.get("last_name")
            player.is_active = row.get("is_active", False)
        else:
            session.add(
                Player(
                    id=row["id"],
                    full_name=row["full_name"],
                    first_name=row.get("first_name"),
                    last_name=row.get("last_name"),
                    is_active=row.get("is_active", False),
                )
            )
        count += 1
    session.commit()
    return count


def ingest_rosters(session: Session, season: str) -> int:
    """Refresh team assignments and bio fields from current-season rosters."""
    teams = list(session.execute(select(Team)).scalars().all())
    updated = 0

    for team in teams:
        roster = commonteamroster.CommonTeamRoster(team_id=team.id, season=season)
        df = roster.get_data_frames()[0]
        time.sleep(0.6)

        for _, row in df.iterrows():
            player_id = int(row["PLAYER_ID"])
            player = session.get(Player, player_id)
            if not player:
                player = Player(
                    id=player_id,
                    full_name=str(row["PLAYER"]),
                    is_active=True,
                )
                session.add(player)

            player.team_id = team.id
            player.position = str(row["POSITION"]) if row["POSITION"] == row["POSITION"] else None
            player.height = str(row["HEIGHT"]) if row["HEIGHT"] == row["HEIGHT"] else None
            player.weight = _parse_weight(row["WEIGHT"])
            player.birth_date = _parse_birth_date(row["BIRTH_DATE"])
            player.is_active = True
            updated += 1

    session.commit()
    return updated


def ingest_players(session: Session, season: str | None = None) -> tuple[int, int]:
    """Full player ingest: static index + roster details for a season."""
    static_count = ingest_players_static(session)
    roster_season = season or "2024-25"
    roster_count = ingest_rosters(session, roster_season)
    return static_count, roster_count
