"""Unit tests for runtime configuration."""

from menu_it.core.config import Settings


def test_default_settings():
    """Verify default runtime settings."""
    settings = Settings(_env_file=None)
    assert settings.app_name == "Menu-It"
    assert settings.app_env == "development"
    assert settings.api_prefix == "/api/v1"


def test_cors_origins_parsing():
    """Verify comma-separated CORS origins parsing."""
    settings = Settings(
        _env_file=None,
        cors_origins_raw="http://localhost:3000, http://localhost:3001",
    )
    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


def test_empty_cors_origins():
    """Verify empty CORS string resolves to empty list."""
    settings = Settings(
        _env_file=None,
        cors_origins_raw="",
    )
    assert settings.cors_origins == []
