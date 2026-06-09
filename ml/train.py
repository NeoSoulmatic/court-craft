"""Train home/away score regressors."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from xgboost import XGBRegressor

from ml.config import (
    ARTIFACTS_DIR,
    FEATURE_COLUMNS,
    FEATURES_DIR,
    MODEL_VERSION,
    TRAIN_SEASONS,
)


def train_models(features: pd.DataFrame) -> dict:
    train_df = features[features["season"].isin(TRAIN_SEASONS)].copy()
    medians = train_df[FEATURE_COLUMNS].median(numeric_only=True)
    train_df[FEATURE_COLUMNS] = train_df[FEATURE_COLUMNS].fillna(medians)

    x = train_df[FEATURE_COLUMNS]
    y_home = train_df["home_score"]
    y_away = train_df["away_score"]

    params = dict(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        objective="reg:squarederror",
    )

    home_model = XGBRegressor(**params)
    away_model = XGBRegressor(**params)
    home_model.fit(x, y_home)
    away_model.fit(x, y_away)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(home_model, ARTIFACTS_DIR / "home_score_model.joblib")
    joblib.dump(away_model, ARTIFACTS_DIR / "away_score_model.joblib")

    meta = {
        "model_version": MODEL_VERSION,
        "train_seasons": TRAIN_SEASONS,
        "train_games": int(len(train_df)),
        "features": FEATURE_COLUMNS,
        "feature_medians": {col: float(medians[col]) for col in FEATURE_COLUMNS},
    }
    (ARTIFACTS_DIR / "model_meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def main() -> None:
    features_path = FEATURES_DIR / "game_features.parquet"
    if not features_path.exists():
        raise FileNotFoundError(f"Missing {features_path}. Run ml/features/build.py first.")
    features = pd.read_parquet(features_path)
    meta = train_models(features)
    print(f"Trained on {meta['train_games']} games -> {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()
