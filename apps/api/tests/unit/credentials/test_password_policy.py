"""Unit tests for password complexity and security policy rules (FCD-05 §6.4)."""

import pytest

from menu_it.credentials.password_policy import validate_password


def test_valid_password_passes():
    """Verify conforming password passes validation without error."""
    validate_password("SecurePassword2026!#$")
    validate_password("correct-horse-battery-staple-1234")


def test_short_password_rejected():
    """Verify password shorter than minimum length of 12 is rejected."""
    with pytest.raises(ValueError, match="at least 12 characters"):
        validate_password("Short123!")


def test_long_password_rejected():
    """Verify password longer than 128 characters is rejected."""
    excessive_password = "a" * 129
    with pytest.raises(ValueError, match="must not exceed 128"):
        validate_password(excessive_password)


def test_surrounding_whitespace_rejected():
    """Verify password with leading or trailing whitespace is rejected."""
    with pytest.raises(ValueError, match="surrounding whitespace"):
        validate_password("  SecurePassword2026!  ")


def test_control_characters_rejected():
    """Verify password containing ASCII control characters is rejected."""
    with pytest.raises(ValueError, match="unsupported control characters"):
        validate_password("SecurePassword\x002026!")
