"""Download historical odds SQLite used for spread/total backtests."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from ml.config import ODDS_DIR, ODDS_SQLITE_PATH, ODDS_SQLITE_URL


def download_odds_db(force: bool = False) -> Path:

    ODDS_DIR.mkdir(parents=True, exist_ok=True)
    if ODDS_SQLITE_PATH.exists() and not force:
        print(f"Odds DB already exists: {ODDS_SQLITE_PATH}")
        return ODDS_SQLITE_PATH

    print(f"Downloading odds data from GitHub...")
    urllib.request.urlretrieve(ODDS_SQLITE_URL, ODDS_SQLITE_PATH)
    print(f"Saved to {ODDS_SQLITE_PATH}")
    return ODDS_SQLITE_PATH


if __name__ == "__main__":
    download_odds_db()
