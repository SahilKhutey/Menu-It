from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_SQLITE_PATH = (BASE_DIR / "modularmenu.db").as_posix()


class Settings(BaseSettings):
    """
    ModularMenu Unified Configuration & Validation Specification (ARC-11 §3.2).
    Enforces strict environment-level validation and credential redaction.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Core Application & Environment
    APP_NAME: str = "ModularMenu"
    PROJECT_NAME: str = "ModularMenu"
    APP_VERSION: str = "1.0.0"
    VERSION: str = "1.0.0"

    APP_ENV: Literal["local", "development", "staging", "production", "test"] = "development"
    ENVIRONMENT: Literal["local", "development", "staging", "production", "test"] = "development"
    DEPLOYMENT_MODE: Literal["managed", "self_hosted"] = "managed"

    APP_DEBUG: bool = False
    DEBUG: bool = False

    # Public URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    PUBLIC_BASE_URL: str = "http://localhost:3000"
    API_PREFIX: str = "/api/v1"
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Session Cookies (ARC-11 §3.2)
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH}"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis (Optional Ephemeral Cache - ARC-11 §11)
    REDIS_ENABLED: bool = False
    REDIS_URL: str | None = None

    # Storage (ARC-11 §10)
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    STORAGE_PROVIDER: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    STORAGE_LOCAL_PATH: str = "./uploads"
    S3_BUCKET_NAME: str | None = None
    S3_BUCKET: str | None = None
    S3_REGION: str = "ap-south-1"
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None

    # Logging & Observability (ARC-11 §16)
    LOG_LEVEL: str = "INFO"

    # Rate Limiting (ARC-07 §9.1)
    PUBLIC_RATE_LIMIT_PER_MINUTE: int = 120
    AUTHENTICATED_RATE_LIMIT_PER_MINUTE: int = 600

    # Customer Hosted Licensing
    LICENSE_KEY: str | None = None
    LICENSE_GRACE_PERIOD_DAYS: int = 30

    @model_validator(mode="after")
    def validate_environment_rules(self) -> "Settings":
        # Normalize environment aliases
        env = (self.APP_ENV or self.ENVIRONMENT or "development").lower()
        self.APP_ENV = env  # type: ignore[assignment]
        self.ENVIRONMENT = env  # type: ignore[assignment]

        # Normalize debug flags
        if self.APP_DEBUG or self.DEBUG:
            debug_val = True
        else:
            debug_val = False

        # T003: Production debug check
        if env == "production" and debug_val:
            raise ValueError("Production configuration violation: debug mode must be disabled.")

        self.APP_DEBUG = debug_val
        self.DEBUG = debug_val

        # T004: Insecure session cookie in production
        if env == "production" and not self.SESSION_COOKIE_SECURE:
            raise ValueError(
                "Production configuration violation: SESSION_COOKIE_SECURE must be true."
            )

        # T005: Redis enabled without URL
        if self.REDIS_ENABLED and not self.REDIS_URL:
            raise ValueError(
                "Invalid configuration: REDIS_ENABLED is true but REDIS_URL is not set."
            )

        # T006: Missing database URL
        if not self.DATABASE_URL or not str(self.DATABASE_URL).strip():
            raise ValueError("Startup rejected: DATABASE_URL must not be empty.")

        # T007: Storage backend validation
        if self.STORAGE_BACKEND not in ("local", "s3"):
            raise ValueError(f"Invalid storage backend: {self.STORAGE_BACKEND}")
        self.STORAGE_PROVIDER = self.STORAGE_BACKEND

        # Normalize URL aliases
        if self.FRONTEND_URL:
            self.PUBLIC_BASE_URL = self.FRONTEND_URL
        if self.API_PREFIX:
            self.API_V1_PREFIX = self.API_PREFIX
        if self.LOCAL_STORAGE_PATH:
            self.STORAGE_LOCAL_PATH = self.LOCAL_STORAGE_PATH
        if self.S3_BUCKET_NAME and not self.S3_BUCKET:
            self.S3_BUCKET = self.S3_BUCKET_NAME

        # T009: Missing/insecure required secret in production/staging
        if env in ("staging", "production"):
            insecure_defaults = (
                "dev-insecure-secret-key-change-in-production-min-32-chars",
                "dev-jwt-super-secret-key-32-chars-long",
                "secret",
            )
            if (
                not self.SECRET_KEY
                or self.SECRET_KEY in insecure_defaults
                or len(self.SECRET_KEY) < 32
            ):
                raise ValueError(
                    f"Startup rejected: {env} environment requires a secure, non-default SECRET_KEY of at least 32 characters."
                )

        return self

    def __repr__(self) -> str:
        """T010: Secret redaction in string representation."""
        attrs = dict(self.__dict__)
        secret_keys = {
            "SECRET_KEY",
            "DATABASE_URL",
            "REDIS_URL",
            "S3_SECRET_KEY",
            "S3_ACCESS_KEY",
            "LICENSE_KEY",
        }
        for k in secret_keys:
            if k in attrs and attrs[k]:
                attrs[k] = "[REDACTED]"
        return f"Settings({attrs})"

    def __str__(self) -> str:
        return self.__repr__()


@lru_cache
def get_settings() -> Settings:
    """Returns singleton cached settings instance (ARC-11 §3.2)."""
    return Settings()


settings = get_settings()
