"""Unit tests for PhoneNumber E.164 parsing and validation (FCD-06 §7.5)."""

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.phone_number import PhoneNumber


def test_phone_number_parse_with_country_code() -> None:
    p = PhoneNumber.parse("+91 98765 43210")
    assert p.e164 == "+919876543210"


def test_phone_number_parse_national_with_region() -> None:
    p = PhoneNumber.parse("9876543210", region="IN")
    assert p.e164 == "+919876543210"


def test_phone_number_invalid_numbers() -> None:
    with pytest.raises(ValidationDomainError):
        PhoneNumber.parse("123")

    with pytest.raises(ValidationDomainError):
        PhoneNumber.parse("invalid-phone")

    with pytest.raises(ValidationDomainError):
        PhoneNumber.parse("")


def test_phone_number_direct_construction_requires_plus() -> None:
    with pytest.raises(ValidationDomainError):
        PhoneNumber("9876543210")
