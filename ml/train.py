"""Train score prediction models. Phase 3."""

from pathlib import Path

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    print("Training pipeline not yet implemented.")
    print("Prerequisites: ETL backfill + ml/features/build.py")


if __name__ == "__main__":
    main()
