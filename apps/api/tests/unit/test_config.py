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


def test_database_settings_defaults():
    """Verify default database configuration parameters (FCD-03 §6.3)."""
    settings = Settings(_env_file=None)
    assert "postgresql+asyncpg" in settings.database_url
    assert settings.database_test_url is None
    assert settings.database_pool_size == 5
    assert settings.database_max_overflow == 10
    assert settings.database_pool_timeout == 30
    assert settings.database_pool_recycle == 1800
    assert settings.database_echo is False


def test_database_custom_settings():
    """Verify custom environment-provided database parameters."""
    settings = Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://user:pass@db:5432/custom_db",
        database_pool_size=15,
        database_max_overflow=25,
        database_echo=True,
    )
    assert settings.database_url == "postgresql+asyncpg://user:pass@db:5432/custom_db"
    assert settings.database_pool_size == 15
    assert settings.database_max_overflow == 25
    assert settings.database_echo is True
