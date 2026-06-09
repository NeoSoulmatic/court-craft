"""Load ML artifacts and run inference."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "ml" / "artifacts"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@lru_cache
def _artifacts_ready() -> bool:
    return (ARTIFACTS_DIR / "home_score_model.joblib").exists()


def get_backtest_metrics() -> dict | None:
    path = ARTIFACTS_DIR / "backtest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def get_model_meta() -> dict | None:
    path = ARTIFACTS_DIR / "model_meta.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def get_predictions(database_url_sync: str) -> list[dict]:
    if not _artifacts_ready():
        return []
    from ml.predict import predict_upcoming

    return predict_upcoming(database_url_sync)
