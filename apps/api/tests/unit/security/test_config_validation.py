"""Tests for production security configuration validation (FCD-11 WP-01 / WP-02)."""

import pytest

from menu_it.core.config import Settings
from menu_it.platform.security.config_validation import (
    SecurityConfigurationError,
    ensure_production_config,
    validate_production_config,
)


def test_validator_detects_insecure_defaults() -> None:
    """Default local settings should produce multiple violations for production deployment."""
    settings = Settings()
    violations = validate_production_config(settings)

    assert len(violations) > 0
    joined = " ".join(violations)
    # Default secret key contains "dev" and "insecure"
    assert "AUTH_SECRET_KEY" in joined
    # Default auth_cookie_secure is False
    assert "AUTH_COOKIE_SECURE" in joined
    # Default database url contains "change_this_local_password"
    assert "DATABASE_URL" in joined


def test_validator_passes_on_hardened_settings() -> None:
    """Hardened settings with strong secrets and TLS enforcement should pass validation."""
    settings = Settings(
        app_env="production",
        app_debug=False,
        auth_secret_key="A_Very_Strong_And_Completely_Random_Production_Secret_Key_2026_!",
        auth_cookie_secure=True,
        auth_cookie_samesite="lax",
        cors_origins_raw="https://app.menu-it.com,https://admin.menu-it.com",
        database_url="postgresql+asyncpg://app_user:StrongRandomPass123!@db.prod.internal:5432/menu_it_prod",
        auth_jwt_algorithm="HS256",
    )
    violations = validate_production_config(settings)
    assert violations == []


def test_validator_detects_debug_mode_and_insecure_cookie() -> None:
    """Validator must catch debug=True and insecure cookies."""
    settings = Settings(
        app_debug=True,
        auth_cookie_secure=False,
    )
    violations = validate_production_config(settings)
    joined = " ".join(violations)
    assert "DEBUG mode" in joined
    assert "AUTH_COOKIE_SECURE" in joined


def test_ensure_production_config_raises_in_production() -> None:
    """ensure_production_config raises SecurityConfigurationError in production."""
    insecure_settings = Settings(app_env="production")
    with pytest.raises(SecurityConfigurationError) as exc_info:
        ensure_production_config(insecure_settings)

    assert len(exc_info.value.violations) > 0


def test_ensure_production_config_silent_in_development() -> None:
    """ensure_production_config should not raise if app_env is development."""
    dev_settings = Settings(app_env="development")
    # Should not raise even with insecure default credentials
    ensure_production_config(dev_settings)
