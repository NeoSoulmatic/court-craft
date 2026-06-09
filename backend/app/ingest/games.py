"""Ingest games and box scores for configured seasons."""

import time
from datetime import datetime

from nba_api.stats.endpoints import leaguegamefinder
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingest.teams import ensure_teams
from app.models.game import Game, TeamGameStats


def _parse_game_id(game_id) -> str:
    return str(game_id).zfill(10)


def _upsert_team_stats(session: Session, game_id: str, row) -> None:
    team_id = int(row["TEAM_ID"])
    matchup: str = row["MATCHUP"]
    is_home = " vs. " in matchup

    existing = session.execute(
        select(TeamGameStats).where(
            TeamGameStats.game_id == game_id,
            TeamGameStats.team_id == team_id,
        )
    ).scalar_one_or_none()

    stats = existing or TeamGameStats(game_id=game_id, team_id=team_id)
    stats.is_home = is_home
    stats.points = int(row["PTS"]) if row["PTS"] == row["PTS"] else None
    stats.fgm = int(row["FGM"]) if row["FGM"] == row["FGM"] else None
    stats.fga = int(row["FGA"]) if row["FGA"] == row["FGA"] else None
    stats.fg_pct = float(row["FG_PCT"]) if row["FG_PCT"] == row["FG_PCT"] else None
    stats.fg3m = int(row["FG3M"]) if row["FG3M"] == row["FG3M"] else None
    stats.fg3a = int(row["FG3A"]) if row["FG3A"] == row["FG3A"] else None
    stats.ftm = int(row["FTM"]) if row["FTM"] == row["FTM"] else None
    stats.fta = int(row["FTA"]) if row["FTA"] == row["FTA"] else None
    stats.oreb = int(row["OREB"]) if row["OREB"] == row["OREB"] else None
    stats.dreb = int(row["DREB"]) if row["DREB"] == row["DREB"] else None
    stats.rebounds = int(row["REB"]) if row["REB"] == row["REB"] else None
    stats.assists = int(row["AST"]) if row["AST"] == row["AST"] else None
    stats.steals = int(row["STL"]) if row["STL"] == row["STL"] else None
    stats.blocks = int(row["BLK"]) if row["BLK"] == row["BLK"] else None
    stats.turnovers = int(row["TOV"]) if row["TOV"] == row["TOV"] else None
    stats.plus_minus = int(row["PLUS_MINUS"]) if row["PLUS_MINUS"] == row["PLUS_MINUS"] else None
    if not existing:
        session.add(stats)


def ingest_season_games(
    session: Session, season: str, season_type: str = "Regular Season"
) -> int:
    """Ingest games for a season and season type (Regular Season or Playoffs)."""
    ensure_teams(session)

    finder = leaguegamefinder.LeagueGameFinder(
        season_nullable=season,
        league_id_nullable="00",
        season_type_nullable=season_type,
    )
    df = finder.get_data_frames()[0]
    time.sleep(0.6)

    count = 0
    for game_id_raw, rows in df.groupby("GAME_ID"):
        game_id = _parse_game_id(game_id_raw)
        if len(rows) < 2:
            continue

        home_rows = rows[rows["MATCHUP"].str.contains(" vs. ", regex=False)]
        away_rows = rows[rows["MATCHUP"].str.contains(" @ ", regex=False)]
        if home_rows.empty or away_rows.empty:
            continue

        home_row = home_rows.iloc[0]
        away_row = away_rows.iloc[0]
        game_date = datetime.strptime(str(home_row["GAME_DATE"]), "%Y-%m-%d").date()

        game = session.get(Game, game_id)
        if not game:
            game = Game(
                id=game_id,
                season=season,
                game_date=game_date,
                home_team_id=int(home_row["TEAM_ID"]),
                away_team_id=int(away_row["TEAM_ID"]),
                home_score=int(home_row["PTS"]),
                away_score=int(away_row["PTS"]),
                status="final",
                season_type=season_type,
            )
            session.add(game)
            count += 1
        else:
            game.home_score = int(home_row["PTS"])
            game.away_score = int(away_row["PTS"])
            game.status = "final"
            game.season_type = season_type

        for _, row in rows.iterrows():
            _upsert_team_stats(session, game_id, row)

    session.commit()
    return count
