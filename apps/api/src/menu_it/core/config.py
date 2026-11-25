"""Centralized backend runtime configuration (FCD-09 WP-01)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/api/src/menu_it/core/config.py -> repository root
PROJECT_ROOT = Path(__file__).resolve().parents[5]


class Settings(BaseSettings):
    """Validated, immutable application settings."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env" if (PROJECT_ROOT / ".env").exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
        frozen=True,
    )

    # Application identity
    app_name: str = "Menu-It"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_debug: bool = False
    app_version: str = "0.1.0"

    # API Server
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_prefix: str = "/api/v1"
    docs_enabled: bool = True

    # CORS
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        validation_alias="CORS_ORIGINS",
    )

    # Localization defaults
    default_locale: str = "en"
    default_timezone: str = "Asia/Kolkata"
    default_currency: str = "INR"

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

    # Authentication & Security configuration (FCD-05)
    auth_issuer: str = Field(
        default="menu-it",
        validation_alias="AUTH_ISSUER",
    )
    auth_audience: str = Field(
        default="menu-it-api",
        validation_alias="AUTH_AUDIENCE",
    )
    auth_access_token_ttl_seconds: int = Field(
        default=600,
        validation_alias="AUTH_ACCESS_TOKEN_TTL_SECONDS",
    )
    auth_refresh_token_ttl_seconds: int = Field(
        default=2592000,
        validation_alias="AUTH_REFRESH_TOKEN_TTL_SECONDS",
    )
    auth_password_reset_ttl_seconds: int = Field(
        default=1800,
        validation_alias="AUTH_PASSWORD_RESET_TTL_SECONDS",
    )
    auth_email_verification_ttl_seconds: int = Field(
        default=86400,
        validation_alias="AUTH_EMAIL_VERIFICATION_TTL_SECONDS",
    )
    auth_max_failed_logins: int = Field(
        default=5,
        validation_alias="AUTH_MAX_FAILED_LOGINS",
    )
    auth_lockout_seconds: int = Field(
        default=900,
        validation_alias="AUTH_LOCKOUT_SECONDS",
    )
    auth_session_idle_timeout_seconds: int = Field(
        default=604800,
        validation_alias="AUTH_SESSION_IDLE_TIMEOUT_SECONDS",
    )
    auth_jwt_algorithm: str = Field(
        default="HS256",
        validation_alias="AUTH_JWT_ALGORITHM",
    )
    auth_secret_key: str = Field(
        default="menu-it-dev-insecure-secret-key-32b-length-at-least",
        validation_alias="AUTH_SECRET_KEY",
    )
    auth_private_key: str | None = Field(
        default=None,
        validation_alias="AUTH_PRIVATE_KEY",
    )
    auth_public_key: str | None = Field(
        default=None,
        validation_alias="AUTH_PUBLIC_KEY",
    )
    auth_key_id: str = Field(
        default="menu-it-k1",
        validation_alias="AUTH_KEY_ID",
    )
    auth_cookie_secure: bool = Field(
        default=False,
        validation_alias="AUTH_COOKIE_SECURE",
    )
    auth_cookie_samesite: str = Field(
        default="lax",
        validation_alias="AUTH_COOKIE_SAMESITE",
    )
    auth_cookie_domain: str | None = Field(
        default=None,
        validation_alias="AUTH_COOKIE_DOMAIN",
    )

    # File Storage configuration (FCD-09 WP-02)
    file_storage_backend: Literal["local", "s3"] = "local"
    file_storage_root: str = "./storage"
    file_max_upload_bytes: int = Field(
        default=10485760,  # 10 MB
        ge=1024,
        le=104857600,  # 100 MB max bound
        validation_alias="FILE_MAX_UPLOAD_BYTES",
    )
    file_allowed_mime_types_raw: str = Field(
        default="image/jpeg,image/png,image/webp,application/pdf",
        validation_alias="FILE_ALLOWED_MIME_TYPES",
    )

    # Notification configuration (FCD-09 WP-03)
    notification_email_enabled: bool = False
    notification_email_provider: Literal["console", "memory", "smtp"] = "console"
    notification_default_from: str = "noreply@menu-it.com"

    # Application Logging (FCD-09 WP-04)
    log_level: str = "INFO"
    log_format: Literal["text", "json"] = "text"

    # Redis & Infrastructure configuration (FCD-10 WP-01)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )
    redis_key_prefix: str = Field(
        default="menu-it:dev",
        validation_alias="REDIS_KEY_PREFIX",
    )
    redis_connect_timeout: int = Field(
        default=5,
        ge=1,
        le=60,
        validation_alias="REDIS_CONNECT_TIMEOUT",
    )
    redis_socket_timeout: int = Field(
        default=5,
        ge=1,
        le=60,
        validation_alias="REDIS_SOCKET_TIMEOUT",
    )
    redis_max_connections: int = Field(
        default=30,
        ge=1,
        le=500,
        validation_alias="REDIS_MAX_CONNECTIONS",
    )

    # Cache configuration (FCD-10 WP-02)
    cache_enabled: bool = Field(
        default=True,
        validation_alias="CACHE_ENABLED",
    )
    cache_default_ttl: int = Field(
        default=300,
        ge=1,
        le=86400,
        validation_alias="CACHE_DEFAULT_TTL",
    )

    # Background Worker configuration (FCD-10 WP-03)
    worker_enabled: bool = Field(
        default=True,
        validation_alias="WORKER_ENABLED",
    )
    worker_max_jobs: int = Field(
        default=10,
        ge=1,
        le=1000,
        validation_alias="WORKER_MAX_JOBS",
    )
    worker_job_timeout: int = Field(
        default=300,
        ge=5,
        le=3600,
        validation_alias="WORKER_JOB_TIMEOUT",
    )
    worker_max_tries: int = Field(
        default=5,
        ge=1,
        le=50,
        validation_alias="WORKER_MAX_TRIES",
    )

    # Event Outbox configuration (FCD-10 WP-05)
    outbox_batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        validation_alias="OUTBOX_BATCH_SIZE",
    )
    outbox_poll_interval: int = Field(
        default=2,
        ge=1,
        le=60,
        validation_alias="OUTBOX_POLL_INTERVAL",
    )

    # Validators
    @field_validator("default_currency", mode="before")
    @classmethod
    def normalize_currency(cls, v: str) -> str:
        code = str(v).strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError(f"Invalid 3-letter currency code: '{v}'.")
        return code

    @field_validator("cors_origins_raw")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        origins = [o.strip() for o in v.split(",") if o.strip()]
        if "*" in origins:
            raise ValueError(
                "Wildcard '*' CORS origin is strictly forbidden for credentialed multi-tenant security."
            )
        return v

    @model_validator(mode="after")
    def validate_production_guards(self) -> "Settings":
        if self.app_env == "production" and self.app_debug:
            raise ValueError("app_debug must be False in production environments.")
        return self

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list of strings."""
        if not self.cors_origins_raw:
            return []
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def file_allowed_mime_types(self) -> set[str]:
        """Parse comma-separated allowed MIME types into a set."""
        if not self.file_allowed_mime_types_raw:
            return set()
        return {
            mime.strip().lower()
            for mime in self.file_allowed_mime_types_raw.split(",")
            if mime.strip()
        }

    def __repr__(self) -> str:
        """Prevent sensitive secrets from leaking into debug prints or logs."""
        return (
            f"Settings(app_name={self.app_name!r}, app_env={self.app_env!r}, "
            f"api_port={self.api_port}, auth_secret_key='[REDACTED]')"
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()


# Convenient global settings reference
settings: Settings = get_settings()
