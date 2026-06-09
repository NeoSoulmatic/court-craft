"""Build leakage-free pre-game features for each game."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ml.config import (
    ELO_HOME_ADV,
    ELO_K,
    ELO_START,
    FEATURE_COLUMNS,
    FEATURES_DIR,
)
from ml.data import load_games
from ml.odds.load import attach_odds, load_odds


@dataclass
class TeamState:
    elo: float = ELO_START
    last_date: pd.Timestamp | None = None
    pts: deque = field(default_factory=lambda: deque(maxlen=20))
    pts_allowed: deque = field(default_factory=lambda: deque(maxlen=20))
    fg_pct: deque = field(default_factory=lambda: deque(maxlen=20))
    pace: deque = field(default_factory=lambda: deque(maxlen=20))


def _pace(fga, fta, tov) -> float:
    if pd.isna(fga) or pd.isna(fta) or pd.isna(tov):
        return np.nan
    return float(fga + 0.44 * fta + tov)


def _rolling_mean(values: deque, window: int) -> float:
    if not values:
        return np.nan
    arr = list(values)[-window:]
    return float(np.mean(arr))


def _expected_home_margin(home_elo: float, away_elo: float) -> float:
    return (home_elo + ELO_HOME_ADV - away_elo) / 25.0


def _update_elo(home_elo: float, away_elo: float, home_margin: float) -> tuple[float, float]:
    expected = _expected_home_margin(home_elo, away_elo)
    delta = ELO_K * (home_margin - expected)
    return home_elo + delta, away_elo - delta


def build_features(database_url_sync: str, odds_path: str | None = None) -> pd.DataFrame:
    games = load_games(database_url_sync)
    odds = load_odds(odds_path)
    games = attach_odds(games, odds)

    teams: dict[int, TeamState] = defaultdict(TeamState)
    rows: list[dict] = []

    for row in games.itertuples(index=False):
        home = teams[row.home_team_id]
        away = teams[row.away_team_id]

        home_rest = (
            (row.game_date - home.last_date).days
            if home.last_date is not None
            else 7
        )
        away_rest = (
            (row.game_date - away.last_date).days
            if away.last_date is not None
            else 7
        )

        feature_row = {
            "game_id": row.game_id,
            "season": row.season,
            "game_date": row.game_date,
            "home_team": row.home_team,
            "away_team": row.away_team,
            "home_score": row.home_score,
            "away_score": row.away_score,
            "spread_home": getattr(row, "spread_home", np.nan),
            "total_line": getattr(row, "total_line", np.nan),
            "home_elo": home.elo,
            "away_elo": away.elo,
            "elo_diff": home.elo + ELO_HOME_ADV - away.elo,
            "home_rest_days": home_rest,
            "away_rest_days": away_rest,
            "rest_diff": home_rest - away_rest,
            "home_roll_pts_10": _rolling_mean(home.pts, 10),
            "away_roll_pts_10": _rolling_mean(away.pts, 10),
            "home_roll_pts_allowed_10": _rolling_mean(home.pts_allowed, 10),
            "away_roll_pts_allowed_10": _rolling_mean(away.pts_allowed, 10),
            "home_roll_fg_pct_10": _rolling_mean(home.fg_pct, 10),
            "away_roll_fg_pct_10": _rolling_mean(away.fg_pct, 10),
            "home_roll_pace_10": _rolling_mean(home.pace, 10),
            "away_roll_pace_10": _rolling_mean(away.pace, 10),
        }
        rows.append(feature_row)

        # Update team state AFTER recording pre-game features
        home_margin = float(row.home_score - row.away_score)
        new_home_elo, new_away_elo = _update_elo(home.elo, away.elo, home_margin)
        home.elo, away.elo = new_home_elo, new_away_elo
        home.last_date = row.game_date
        away.last_date = row.game_date

        home_fga, away_fga = row.home_fga, row.away_fga
        home_fgm, away_fgm = row.home_fgm, row.away_fgm
        home_fta, away_fta = row.home_fta, row.away_fta
        home_tov, away_tov = row.home_tov, row.away_tov

        home.pts.append(float(row.home_score))
        away.pts.append(float(row.away_score))
        home.pts_allowed.append(float(row.away_score))
        away.pts_allowed.append(float(row.home_score))
        if home_fga and home_fga > 0:
            home.fg_pct.append(float(home_fgm) / float(home_fga))
        if away_fga and away_fga > 0:
            away.fg_pct.append(float(away_fgm) / float(away_fga))
        home.pace.append(_pace(home_fga, home_fta, home_tov))
        away.pace.append(_pace(away_fga, away_fta, away_tov))

    df = pd.DataFrame(rows)
    return df


def save_features(df: pd.DataFrame, path=None) -> Path:
    from pathlib import Path

    out = path or FEATURES_DIR / "game_features.parquet"
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    return out


def main() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from backend.app.core.config import get_settings

    settings = get_settings()
    df = build_features(settings.database_url_sync)
    out = save_features(df)
    print(f"Built features for {len(df)} games -> {out}")
    print(f"Columns: {FEATURE_COLUMNS}")


if __name__ == "__main__":
    main()
