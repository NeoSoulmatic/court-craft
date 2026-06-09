"""Generate predictions for upcoming scheduled games."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from collections import defaultdict

from ml.config import ARTIFACTS_DIR, ELO_HOME_ADV, FEATURE_COLUMNS, MODEL_VERSION
from ml.data import load_games
from ml.features.build import TeamState, _pace, _rolling_mean, _update_elo


def _load_scheduled(database_url_sync: str) -> pd.DataFrame:
    query = text(
        """
        SELECT
            g.id AS game_id,
            g.season,
            g.season_type,
            g.game_date,
            g.home_team_id,
            g.away_team_id,
            ht.full_name AS home_team,
            at.full_name AS away_team
        FROM games g
        JOIN teams ht ON ht.id = g.home_team_id
        JOIN teams at ON at.id = g.away_team_id
        WHERE g.status = 'scheduled'
        ORDER BY g.game_date, g.id
        """
    )
    engine = create_engine(database_url_sync)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    if not df.empty:
        df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def _build_team_states(database_url_sync: str) -> dict[int, TeamState]:
    # Replay all completed games (regular + playoffs) for current form
    games = load_games(database_url_sync, regular_season_only=False)
    teams: dict[int, TeamState] = defaultdict(TeamState)

    for row in games.itertuples(index=False):
        home = teams[row.home_team_id]
        away = teams[row.away_team_id]
        home_margin = float(row.home_score - row.away_score)
        home.elo, away.elo = _update_elo(home.elo, away.elo, home_margin)
        home.last_date = row.game_date
        away.last_date = row.game_date
        home.pts.append(float(row.home_score))
        away.pts.append(float(row.away_score))
        home.pts_allowed.append(float(row.away_score))
        away.pts_allowed.append(float(row.home_score))
        if row.home_fga and row.home_fga > 0:
            home.fg_pct.append(float(row.home_fgm) / float(row.home_fga))
        if row.away_fga and row.away_fga > 0:
            away.fg_pct.append(float(row.away_fgm) / float(row.away_fga))
        home.pace.append(_pace(row.home_fga, row.home_fta, row.home_tov))
        away.pace.append(_pace(row.away_fga, row.away_fta, row.away_tov))
    return teams


def predict_upcoming(database_url_sync: str) -> list[dict]:
    home_model = joblib.load(ARTIFACTS_DIR / "home_score_model.joblib")
    away_model = joblib.load(ARTIFACTS_DIR / "away_score_model.joblib")
    meta_path = ARTIFACTS_DIR / "model_meta.json"
    medians = None
    if meta_path.exists():
        import json

        medians = json.loads(meta_path.read_text()).get("feature_medians")

    scheduled = _load_scheduled(database_url_sync)
    if scheduled.empty:
        return []

    teams = _build_team_states(database_url_sync)
    predictions: list[dict] = []

    for row in scheduled.itertuples(index=False):
        home = teams[row.home_team_id]
        away = teams[row.away_team_id]
        home_rest = (row.game_date - home.last_date).days if home.last_date is not None else 7
        away_rest = (row.game_date - away.last_date).days if away.last_date is not None else 7

        features = {
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
        x = pd.DataFrame([features])[FEATURE_COLUMNS]
        if medians:
            x = x.fillna(medians)
        pred_home = float(home_model.predict(x)[0])
        pred_away = float(away_model.predict(x)[0])
        margin = pred_home - pred_away
        total = pred_home + pred_away
        win_prob = float(1.0 / (1.0 + np.exp(-margin / 11.0)))

        is_playoff = getattr(row, "season_type", "Regular Season") == "Playoffs"
        predictions.append(
            {
                "game_id": row.game_id,
                "game_date": str(
                    row.game_date.date() if hasattr(row.game_date, "date") else row.game_date
                ),
                "season_type": getattr(row, "season_type", "Regular Season"),
                "home_team": row.home_team,
                "away_team": row.away_team,
                "home_win_prob": round(win_prob, 4),
                "predicted_home_score": round(pred_home, 1),
                "predicted_away_score": round(pred_away, 1),
                "predicted_spread": round(-margin, 1),  # home favored => negative
                "predicted_total": round(total, 1),
                "model_version": MODEL_VERSION,
                "note": (
                    "Playoff projection — model trained on regular season only."
                    if is_playoff
                    else None
                ),
            }
        )
    return predictions


def main() -> None:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from backend.app.core.config import get_settings

    settings = get_settings()
    preds = predict_upcoming(settings.database_url_sync)
    out = ARTIFACTS_DIR / "upcoming_predictions.json"
    out.write_text(json.dumps(preds, indent=2))
    print(f"Wrote {len(preds)} predictions -> {out}")


if __name__ == "__main__":
    main()
