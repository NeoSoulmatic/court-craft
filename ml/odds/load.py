"""Load and normalize historical odds from kyleskom OddsData.sqlite."""

from __future__ import annotations

import re
import sqlite3

import pandas as pd

from ml.config import ALL_SEASONS, ODDS_SQLITE_PATH

# Table naming varies by season in the upstream SQLite file
ODDS_TABLE_BY_SEASON = {
    "2022-23": "odds_2022-23",
    "2023-24": "2023-24",
    "2024-25": "2024-25",
    "2025-26": "odds_2025-26",
}


def _parse_odds_date(value: str, season: str) -> pd.Timestamp:
    text = str(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return pd.to_datetime(text)
    # e.g. 2022-23-1019
    match = re.fullmatch(r"(\d{4})-\d{2}-(\d{4})", text)
    if match:
        year = int(match.group(1))
        month_day = match.group(2)
        return pd.to_datetime(f"{year}-{month_day[:2]}-{month_day[2:]}")
    return pd.to_datetime(text, errors="coerce")


def load_odds(sqlite_path: str | None = None) -> pd.DataFrame:
    path = sqlite_path or str(ODDS_SQLITE_PATH)
    conn = sqlite3.connect(path)
    frames: list[pd.DataFrame] = []

    for season in ALL_SEASONS:
        table = ODDS_TABLE_BY_SEASON.get(season)
        if not table:
            continue
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
        except Exception:
            continue
        if df.empty:
            continue
        df["season"] = season
        df["game_date"] = df["Date"].apply(lambda v: _parse_odds_date(v, season))
        df["home_team"] = df["Home"].astype(str)
        df["away_team"] = df["Away"].astype(str)
        df["spread_home"] = pd.to_numeric(df["Spread"], errors="coerce")
        df["total_line"] = pd.to_numeric(df["OU"], errors="coerce")
        frames.append(
            df[["season", "game_date", "home_team", "away_team", "spread_home", "total_line"]]
        )

    conn.close()
    if not frames:
        return pd.DataFrame()

    odds = pd.concat(frames, ignore_index=True)
    odds = odds.dropna(subset=["game_date", "spread_home", "total_line"])
    odds = odds.drop_duplicates(subset=["season", "game_date", "home_team", "away_team"])
    return odds.reset_index(drop=True)


def attach_odds(games: pd.DataFrame, odds: pd.DataFrame) -> pd.DataFrame:
    if odds.empty:
        games = games.copy()
        games["spread_home"] = pd.NA
        games["total_line"] = pd.NA
        return games

    merged = games.merge(
        odds,
        on=["season", "game_date", "home_team", "away_team"],
        how="left",
    )
    return merged
