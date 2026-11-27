"""Unit tests for email address normalization (FCD-05 §5.1)."""

import pytest

from menu_it.database.models.user import normalize_email


def test_email_normalization_lowercases_and_strips():
    """Verify email normalization handles casing and whitespace cleanly."""
    assert normalize_email("  User.Name@Example.COM  ") == "user.name@example.com"
    assert normalize_email("Admin@restaurant.org") == "admin@restaurant.org"


def test_email_normalization_rejects_empty():
    """Verify empty or blank email raises ValueError."""
    with pytest.raises(ValueError, match="Email is required"):
        normalize_email("")
    with pytest.raises(ValueError, match="Email is required"):
        normalize_email("   ")
