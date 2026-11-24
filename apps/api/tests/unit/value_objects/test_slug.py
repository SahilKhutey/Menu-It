"""Unit tests for Slug value object (FCD-06 §7.6)."""

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.slug import Slug


def test_slug_valid_and_normalized() -> None:
    s = Slug("  My-Awesome-Restaurant-123  ")
    assert s.value == "my-awesome-restaurant-123"


def test_slug_invalid_formats() -> None:
    with pytest.raises(ValidationDomainError):
        Slug("")

    with pytest.raises(ValidationDomainError):
        Slug("has spaces")

    with pytest.raises(ValidationDomainError):
        Slug("-starts-with-hyphen")

    with pytest.raises(ValidationDomainError):
        Slug("ends-with-hyphen-")

    with pytest.raises(ValidationDomainError):
        Slug("double--hyphens")

    with pytest.raises(ValidationDomainError):
        Slug("special_characters!")


def test_slug_max_length() -> None:
    too_long = "a" * 101
    with pytest.raises(ValidationDomainError):
        Slug(too_long)
