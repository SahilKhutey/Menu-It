"""Unit tests for centralized runtime configuration (FCD-09 WP-01)."""

import pytest
from pydantic import ValidationError

from menu_it.core.config import Settings


def test_default_settings_are_valid():
    """Default settings instantiate cleanly in test environment."""
    cfg = Settings(app_env="test")
    assert cfg.app_name == "Menu-It"
    assert cfg.api_port == 8000
    assert cfg.default_currency == "INR"
    assert "image/png" in cfg.file_allowed_mime_types
    assert cfg.file_max_upload_bytes == 10485760


def test_invalid_port_is_rejected():
    """Ports outside valid TCP range [1, 65535] must fail validation."""
    with pytest.raises(ValidationError):
        Settings(api_port=70000, app_env="test")

    with pytest.raises(ValidationError):
        Settings(api_port=0, app_env="test")


def test_wildcard_cors_is_rejected():
    """Wildcard CORS origin is disallowed for multi-tenant credential security."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(cors_origins_raw="http://localhost:3000,*", app_env="test")
    assert "Wildcard '*' CORS origin is strictly forbidden" in str(exc_info.value)


def test_currency_code_is_normalized_and_validated():
    """Currency is normalized to uppercase and validated as 3 alphabetic chars."""
    cfg = Settings(default_currency="inr", app_env="test")
    assert cfg.default_currency == "INR"

    with pytest.raises(ValidationError):
        Settings(default_currency="INVALID", app_env="test")

    with pytest.raises(ValidationError):
        Settings(default_currency="12$", app_env="test")


def test_production_debug_guard():
    """Debug mode is rejected in production environments."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(app_env="production", app_debug=True)
    assert "app_debug must be False in production" in str(exc_info.value)


def test_file_upload_limit_bounds():
    """Upload byte limit must be bounded within [1KB, 100MB]."""
    with pytest.raises(ValidationError):
        Settings(file_max_upload_bytes=100, app_env="test")  # < 1024

    with pytest.raises(ValidationError):
        Settings(file_max_upload_bytes=200000000, app_env="test")  # > 100MB


def test_settings_immutability():
    """Settings instance is frozen and cannot be mutated at runtime."""
    cfg = Settings(app_env="test")
    with pytest.raises(ValidationError):
        cfg.app_name = "Modified Name"  # type: ignore[misc]


def test_secrets_redacted_in_repr():
    """Secret keys must not leak in string representations."""
    cfg = Settings(app_env="test", auth_secret_key="super-secret-key-12345")
    rep = repr(cfg)
    assert "super-secret-key-12345" not in rep
    assert "[REDACTED]" in rep


def test_allowed_mime_types_property():
    """Parsing comma-separated MIME types returns a clean lowercase set."""
    cfg = Settings(
        file_allowed_mime_types_raw="image/jpeg, IMAGE/PNG , application/pdf",
        app_env="test",
    )
    assert cfg.file_allowed_mime_types == {"image/jpeg", "image/png", "application/pdf"}
