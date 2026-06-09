"""ML pipeline configuration."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
ODDS_DIR = DATA_DIR / "odds"
FEATURES_DIR = DATA_DIR / "features"
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"

TRAIN_SEASONS = ["2022-23", "2023-24", "2024-25"]
TEST_SEASON = "2025-26"
ALL_SEASONS = TRAIN_SEASONS + [TEST_SEASON]

# Regular season only for v1; playoffs in v2
REGULAR_SEASON_ONLY = True

ELO_START = 1500.0
ELO_K = 20.0
ELO_HOME_ADV = 90.0
ROLLING_WINDOWS = (5, 10, 20)

ODDS_SQLITE_URL = (
    "https://raw.githubusercontent.com/kyleskom/NBA-Machine-Learning-Sports-Betting/"
    "master/Data/OddsData.sqlite"
)
ODDS_SQLITE_PATH = ODDS_DIR / "OddsData.sqlite"

FEATURE_COLUMNS = [
    "home_elo",
    "away_elo",
    "elo_diff",
    "home_rest_days",
    "away_rest_days",
    "rest_diff",
    "home_roll_pts_10",
    "away_roll_pts_10",
    "home_roll_pts_allowed_10",
    "away_roll_pts_allowed_10",
    "home_roll_fg_pct_10",
    "away_roll_fg_pct_10",
    "home_roll_pace_10",
    "away_roll_pace_10",
]

MODEL_VERSION = "xgb_v1"
