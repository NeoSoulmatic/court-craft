from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://courtcraft:courtcraft@localhost:5433/courtcraft"
    database_url_sync: str = "postgresql://courtcraft:courtcraft@localhost:5433/courtcraft"
    cors_origins: str = "http://localhost:5173"
    seasons_backfill: str = "2022-23,2023-24,2024-25,2025-26"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def seasons_list(self) -> list[str]:
        return [season.strip() for season in self.seasons_backfill.split(",") if season.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
