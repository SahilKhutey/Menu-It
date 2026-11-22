from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_SQLITE_PATH = (BASE_DIR / "modularmenu.db").as_posix()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core Application
    PROJECT_NAME: str = "ModularMenu"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEPLOYMENT_MODE: Literal["managed", "self_hosted"] = "managed"
    DEBUG: bool = True

    # Public URLs
    PUBLIC_BASE_URL: str = "http://localhost:3000"
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH}"
    # In production PostgreSQL: "postgresql+asyncpg://postgres:password@localhost:5432/modularmenu"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Storage
    STORAGE_PROVIDER: Literal["local", "s3"] = "local"
    STORAGE_LOCAL_PATH: str = "./uploads"
    S3_BUCKET: str | None = None
    S3_REGION: str = "ap-south-1"
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None

    # Rate Limiting (ARC-07 §9.1)
    PUBLIC_RATE_LIMIT_PER_MINUTE: int = 120
    AUTHENTICATED_RATE_LIMIT_PER_MINUTE: int = 600

    # Customer Hosted Licensing
    LICENSE_KEY: str | None = None
    LICENSE_GRACE_PERIOD_DAYS: int = 30


settings = Settings()
