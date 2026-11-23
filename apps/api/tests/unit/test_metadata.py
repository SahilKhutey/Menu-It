"""Unit tests for application metadata constants."""

from menu_it.core.metadata import API_VERSION, APP_DESCRIPTION, APP_TITLE


def test_metadata_constants():
    """Verify application title, version, and description."""
    assert APP_TITLE == "Menu-It API"
    assert API_VERSION == "0.1.0"
    assert "Menu-It" in APP_DESCRIPTION
