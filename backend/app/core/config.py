import os
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
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
    odds_api_key: str | None = None
    odds_api_regions: str = "us"
    odds_cache_hours: int = 6
    serve_static: bool = False
    port: int = 8000

    @model_validator(mode="after")
    def apply_platform_env(self) -> "Settings":
        """Map Render/Heroku DATABASE_URL and optional PORT."""
        raw_db = os.getenv("DATABASE_URL")
        if raw_db:
            sync = raw_db.replace("postgresql+asyncpg://", "postgresql://", 1).replace(
                "postgres://", "postgresql://", 1
            )
            object.__setattr__(self, "database_url_sync", sync)
            object.__setattr__(
                self,
                "database_url",
                sync.replace("postgresql://", "postgresql+asyncpg://", 1),
            )

        raw_port = os.getenv("PORT")
        if raw_port:
            object.__setattr__(self, "port", int(raw_port))

        if os.getenv("SERVE_STATIC", "").lower() in ("1", "true", "yes"):
            object.__setattr__(self, "serve_static", True)

        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def seasons_list(self) -> list[str]:
        return [season.strip() for season in self.seasons_backfill.split(",") if season.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
