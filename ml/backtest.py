"""Backtest on held-out season (2025-26)."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ml.config import (
    ARTIFACTS_DIR,
    FEATURE_COLUMNS,
    FEATURES_DIR,
    MODEL_VERSION,
    TEST_SEASON,
    TRAIN_SEASONS,
)


def _home_win_prob(margin: float, scale: float = 11.0) -> float:
    # Logistic mapping from predicted margin to win probability
    return float(1.0 / (1.0 + np.exp(-margin / scale)))


def run_backtest(features: pd.DataFrame) -> dict:
    home_model = joblib.load(ARTIFACTS_DIR / "home_score_model.joblib")
    away_model = joblib.load(ARTIFACTS_DIR / "away_score_model.joblib")

    train_medians = features[features["season"].isin(TRAIN_SEASONS)][FEATURE_COLUMNS].median(numeric_only=True)
    test_df = features[features["season"] == TEST_SEASON].copy()
    test_df[FEATURE_COLUMNS] = test_df[FEATURE_COLUMNS].fillna(train_medians)
    x = test_df[FEATURE_COLUMNS]
    pred_home = home_model.predict(x)
    pred_away = away_model.predict(x)

    test_df = test_df.assign(
        pred_home=pred_home,
        pred_away=pred_away,
        pred_margin=pred_home - pred_away,
        pred_total=pred_home + pred_away,
        actual_margin=test_df["home_score"] - test_df["away_score"],
        actual_total=test_df["home_score"] + test_df["away_score"],
    )

    ml_hits = (test_df["pred_margin"] > 0) == (test_df["actual_margin"] > 0)
    ml_push = test_df["actual_margin"] == 0
    ml_acc = float(ml_hits[~ml_push].mean()) if (~ml_push).any() else 0.0

    odds_df = test_df.dropna(subset=["spread_home", "total_line"])
    spread_hits = (odds_df["actual_margin"] + odds_df["spread_home"]) > 0
    spread_pushes = (odds_df["actual_margin"] + odds_df["spread_home"]) == 0
    spread_rate = (
        float(spread_hits[~spread_pushes].mean()) if (~spread_pushes).any() else None
    )

    pred_spread_covers = (odds_df["pred_margin"] + odds_df["spread_home"]) > 0
    spread_model_rate = (
        float(pred_spread_covers[~spread_pushes].mean()) if (~spread_pushes).any() else None
    )

    total_over_actual = odds_df["actual_total"] > odds_df["total_line"]
    total_push = odds_df["actual_total"] == odds_df["total_line"]
    total_rate = (
        float(total_over_actual[~total_push].mean()) if (~total_push).any() else None
    )

    pred_over = odds_df["pred_total"] > odds_df["total_line"]
    total_model_rate = (
        float(pred_over[~total_push].mean()) if (~total_push).any() else None
    )

    margin_mae = float(np.mean(np.abs(test_df["pred_margin"] - test_df["actual_margin"])))
    total_mae = float(np.mean(np.abs(test_df["pred_total"] - test_df["actual_total"])))

    return {
        "model_version": MODEL_VERSION,
        "train_seasons": TRAIN_SEASONS,
        "test_season": TEST_SEASON,
        "regular_season_only": True,
        "moneyline": {
            "accuracy": round(ml_acc, 4),
            "games": int((~ml_push).sum()),
        },
        "spread": {
            "games_with_odds": int(len(odds_df)),
            "vegas_baseline_over_50": round(spread_rate, 4) if spread_rate is not None else None,
            "model_pick_hit_rate": round(spread_model_rate, 4) if spread_model_rate else None,
            "note": "Model picks home cover when pred_margin + spread_home > 0",
        },
        "total": {
            "games_with_odds": int(len(odds_df)),
            "vegas_over_rate": round(total_rate, 4) if total_rate is not None else None,
            "model_over_hit_rate": round(total_model_rate, 4) if total_model_rate else None,
        },
        "errors": {
            "margin_mae": round(float(margin_mae), 2) if margin_mae == margin_mae else 0.0,
            "total_mae": round(float(total_mae), 2) if total_mae == total_mae else 0.0,
        },
        "odds_source": "kyleskom/NBA-Machine-Learning-Sports-Betting OddsData.sqlite (SBR closing lines)",
        "odds_coverage_note": (
            f"{len(odds_df)} of {len(test_df)} {TEST_SEASON} games had closing lines in the free odds file."
        ),
    }


def main() -> None:
    features_path = FEATURES_DIR / "game_features.parquet"
    features = pd.read_parquet(features_path)
    results = run_backtest(features)
    out = ARTIFACTS_DIR / "backtest.json"
    out.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
