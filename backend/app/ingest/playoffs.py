"""Ingest NBA playoff games and upcoming schedule."""

import time
from datetime import datetime

from nba_api.stats.endpoints import leaguegamefinder, scheduleleaguev2
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ingest.games import _parse_game_id, _upsert_team_stats, ingest_season_games
from app.ingest.teams import ensure_teams
from app.models.game import Game


def ensure_season_type_column(session: Session) -> None:
    session.execute(
        text(
            "ALTER TABLE games ADD COLUMN IF NOT EXISTS season_type "
            "VARCHAR(20) DEFAULT 'Regular Season'"
        )
    )
    session.execute(
        text(
            "UPDATE games SET season_type = 'Playoffs' "
            "WHERE id LIKE '004%' AND (season_type IS NULL OR season_type = 'Regular Season')"
        )
    )
    session.execute(
        text(
            "UPDATE games SET season_type = 'Regular Season' "
            "WHERE id LIKE '002%' AND season_type IS NULL"
        )
    )
    session.commit()


def ingest_playoff_results(session: Session, season: str) -> int:
    """Ingest completed playoff games with box scores."""
    ensure_teams(session)
    count = ingest_season_games(session, season, season_type="Playoffs")
    return count


def ingest_playoff_schedule(session: Session, season: str) -> int:
    """Upsert scheduled playoff games from league schedule (e.g. upcoming Finals)."""
    ensure_teams(session)
    schedule = scheduleleaguev2.ScheduleLeagueV2(season=season)
    df = schedule.get_data_frames()[0]
    time.sleep(0.6)

    playoff_df = df[df["gameId"].astype(str).str.startswith("004")]
    added = 0

    for _, row in playoff_df.iterrows():
        game_id = _parse_game_id(row["gameId"])
        status_text = str(row["gameStatusText"])
        is_final = int(row["gameStatus"]) == 3 or status_text.startswith("Final")

        raw_date = str(row["gameDate"])[:10]
        game_date = datetime.strptime(raw_date, "%m/%d/%Y").date()
        home_team_id = int(row["homeTeam_teamId"])
        away_team_id = int(row["awayTeam_teamId"])

        game = session.get(Game, game_id)
        if game:
            if not is_final:
                game.status = "scheduled"
                game.season_type = "Playoffs"
            continue

        if is_final:
            continue  # completed games come from leaguegamefinder

        game = Game(
            id=game_id,
            season=season,
            game_date=game_date,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_score=None,
            away_score=None,
            status="scheduled",
            season_type="Playoffs",
        )
        session.add(game)
        added += 1

    session.commit()
    return added


def ingest_playoffs(session: Session, season: str) -> tuple[int, int]:
    results = ingest_playoff_results(session, season)
    scheduled = ingest_playoff_schedule(session, season)
    return results, scheduled


def ingest_all_playoffs(session: Session, seasons: list[str]) -> int:
    ensure_season_type_column(session)
    total = 0
    for season in seasons:
        results, scheduled = ingest_playoffs(session, season)
        total += results + scheduled
        print(f"  {season}: {results} result rows, {scheduled} scheduled added")
        time.sleep(0.8)
    return total
