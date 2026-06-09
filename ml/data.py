"""Load game data from PostgreSQL into pandas."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text

from ml.config import ALL_SEASONS, REGULAR_SEASON_ONLY


def load_games(database_url_sync: str, *, regular_season_only: bool = True) -> pd.DataFrame:
    seasons_sql = ", ".join(f"'{s}'" for s in ALL_SEASONS)
    season_type_filter = "AND g.season_type = 'Regular Season'" if regular_season_only else ""
    query = text(
        f"""
        SELECT
            g.id AS game_id,
            g.season,
            g.game_date,
            g.home_team_id,
            g.away_team_id,
            ht.full_name AS home_team,
            at.full_name AS away_team,
            ht.abbreviation AS home_abbr,
            at.abbreviation AS away_abbr,
            g.home_score,
            g.away_score,
            g.status,
            g.season_type,
            hts.fga AS home_fga,
            ats.fga AS away_fga,
            hts.fgm AS home_fgm,
            ats.fgm AS away_fgm,
            hts.fta AS home_fta,
            ats.fta AS away_fta,
            hts.turnovers AS home_tov,
            ats.turnovers AS away_tov,
            hts.fg3a AS home_fg3a,
            ats.fg3a AS away_fg3a
        FROM games g
        JOIN teams ht ON ht.id = g.home_team_id
        JOIN teams at ON at.id = g.away_team_id
        LEFT JOIN team_game_stats hts ON hts.game_id = g.id AND hts.team_id = g.home_team_id
        LEFT JOIN team_game_stats ats ON ats.game_id = g.id AND ats.team_id = g.away_team_id
        WHERE g.season IN ({seasons_sql})
          AND g.status = 'final'
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
          {season_type_filter}
        ORDER BY g.game_date, g.id
        """
    )
    engine = create_engine(database_url_sync)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df["game_date"] = pd.to_datetime(df["game_date"])
    if regular_season_only and REGULAR_SEASON_ONLY:
        df = df[df["season_type"] == "Regular Season"]
    return df.reset_index(drop=True)
