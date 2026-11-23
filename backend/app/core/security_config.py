"""
ModularMenu — Security Configuration & Settings (ARC-12 §30.1).
Strict validation of environment-specific security controls.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    """System-wide security configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: Literal["local", "development", "staging", "production"] = "local"
    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    CSRF_ENABLED: bool = True
    SESSION_COOKIE_NAME: str = "__Host-modularmenu_session"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    SESSION_MAX_AGE_SECONDS: int = 14 * 86400  # 14 days
    SESSION_IDLE_TIMEOUT_SECONDS: int = 86400  # 24 hours
    LOGIN_ATTEMPT_LIMIT: int = 5
    LOGIN_WINDOW_SECONDS: int = 300
    REQUEST_BODY_LIMIT_BYTES: int = 10 * 1024 * 1024  # 10 MB
    TRUSTED_PROXY_CIDRS: list[str] = Field(default_factory=lambda: ["127.0.0.1", "::1"])

    def validate_production_security(self) -> None:
        """Enforce strict production invariants (ARC12-D14, ARC11-I08)."""
        if self.ENVIRONMENT == "production":
            if not self.SESSION_COOKIE_SECURE:
                raise ValueError("SESSION_COOKIE_SECURE must be True in production")
            for origin in self.ALLOWED_ORIGINS:
                if origin != "*" and not origin.startswith("https://"):
                    raise ValueError(
                        f"Insecure origin {origin} forbidden in production; HTTPS required"
                    )
                if origin == "*":
                    raise ValueError("Wildcard CORS origin '*' forbidden in production")


security_settings = SecuritySettings()
