"""Centralized backend runtime configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/api/src/menu_it/core/config.py -> repository root
PROJECT_ROOT = Path(__file__).resolve().parents[5]


class Settings(BaseSettings):
    """Validated application settings."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env" if (PROJECT_ROOT / ".env").exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "Menu-It"
    app_env: str = "development"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    docs_enabled: bool = True
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        validation_alias="CORS_ORIGINS",
    )

    # Database configuration (FCD-03)
    database_url: str = Field(
        default="postgresql+asyncpg://menu_it:change_this_local_password@localhost:5432/menu_it",
        validation_alias="DATABASE_URL",
    )
    database_test_url: str | None = Field(
        default=None,
        validation_alias="DATABASE_TEST_URL",
    )
    database_pool_size: int = Field(
        default=5,
        validation_alias="DATABASE_POOL_SIZE",
        ge=1,
        le=50,
    )
    database_max_overflow: int = Field(
        default=10,
        validation_alias="DATABASE_MAX_OVERFLOW",
        ge=0,
        le=100,
    )
    database_pool_timeout: int = Field(
        default=30,
        validation_alias="DATABASE_POOL_TIMEOUT",
        ge=1,
        le=300,
    )
    database_pool_recycle: int = Field(
        default=1800,
        validation_alias="DATABASE_POOL_RECYCLE",
        ge=60,
        le=7200,
    )
    database_echo: bool = Field(
        default=False,
        validation_alias="DATABASE_ECHO",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list of strings."""
        if not self.cors_origins_raw:
            return []
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()


# Convenient global settings reference
settings: Settings = get_settings()
