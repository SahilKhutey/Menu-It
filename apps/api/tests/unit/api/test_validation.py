"""Unit tests for validation error normalization (FCD-07 WP-04)."""

from menu_it.api.exceptions.handlers import normalize_validation_error


def test_normalize_validation_error_strips_body_prefix():
    raw_error = {
        "type": "string_too_short",
        "loc": ("body", "name"),
        "msg": "String should have at least 1 character",
        "input": "a",
    }
    normalized = normalize_validation_error(raw_error)
    assert normalized.field == "name"
    assert normalized.code == "string_too_short"
    assert "at least 1 character" in normalized.message


def test_normalize_validation_error_nested_field():
    raw_error = {
        "type": "value_error",
        "loc": ("body", "address", "postal_code"),
        "msg": "Invalid postal code format",
        "input": "000000",
    }
    normalized = normalize_validation_error(raw_error)
    assert normalized.field == "address.postal_code"
    assert normalized.code == "value_error"
