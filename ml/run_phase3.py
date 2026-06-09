#!/usr/bin/env python3
"""Run full Phase 3 pipeline: odds -> features -> train -> backtest -> predict."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.core.config import get_settings
from ml.backtest import main as backtest_main
from ml.features.build import build_features, save_features
from ml.odds.download import download_odds_db
from ml.predict import main as predict_main
from ml.train import main as train_main


def main() -> None:
    settings = get_settings()
    print("=== Phase 3: Court Craft ML pipeline ===\n")

    print("1/5 Download odds (if needed)...")
    download_odds_db()

    print("2/5 Build features...")
    df = build_features(settings.database_url_sync)
    path = save_features(df)
    print(f"    {len(df)} games -> {path}")

    print("3/5 Train models...")
    train_main()

    print("4/5 Backtest...")
    backtest_main()

    print("5/5 Predict upcoming...")
    predict_main()

    print("\nPhase 3 complete.")


if __name__ == "__main__":
    main()
