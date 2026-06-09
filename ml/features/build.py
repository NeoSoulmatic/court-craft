"""Feature engineering for game prediction.

Phase 3: implement rolling team stats, rest days, home court, Elo.
Run after ETL backfill completes.
"""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "features"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Feature builder not yet implemented.")
    print(f"Output will go to: {DATA_DIR}")
    print("See ml/README.md for the feature list.")


if __name__ == "__main__":
    main()
