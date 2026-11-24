"""Unit tests for Contact and EmailAddress value objects (FCD-06 §7.4)."""

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.contact import EmailAddress


def test_email_address_valid_and_normalization() -> None:
    e = EmailAddress("  Test.User@Example.COM  ")
    assert e.value == "test.user@example.com"


def test_email_address_invalid_formats() -> None:
    with pytest.raises(ValidationDomainError):
        EmailAddress("")

    with pytest.raises(ValidationDomainError):
        EmailAddress("notanemail")

    with pytest.raises(ValidationDomainError):
        EmailAddress("@example.com")

    with pytest.raises(ValidationDomainError):
        EmailAddress("user@")

    with pytest.raises(ValidationDomainError):
        EmailAddress(123)  # type: ignore[arg-type]


def test_email_address_length_limit() -> None:
    long_email = "a" * 315 + "@example.com"
    with pytest.raises(ValidationDomainError):
        EmailAddress(long_email)
