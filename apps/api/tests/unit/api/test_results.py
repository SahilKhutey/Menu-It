"""Unit tests for ApplicationResult container (FCD-07 WP-12)."""

import pytest

from menu_it.services.results import ApplicationResult


def test_application_result_success():
    res = ApplicationResult.ok("hello world")
    assert res.is_success
    assert not res.is_failure
    assert res.value == "hello world"
    assert res.unwrap() == "hello world"
    assert res.unwrap_or("fallback") == "hello world"
    assert res.error is None


def test_application_result_failure():
    res = ApplicationResult.fail("Entity missing", error_code="NOT_FOUND")
    assert not res.is_success
    assert res.is_failure
    assert res.error == "Entity missing"
    assert res.error_code == "NOT_FOUND"
    assert res.unwrap_or("fallback") == "fallback"

    with pytest.raises(ValueError, match="Cannot get value of failed ApplicationResult"):
        _ = res.value
