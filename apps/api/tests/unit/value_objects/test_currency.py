"""Unit tests for Currency value object (FCD-06 §7.1)."""

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.currency import Currency


def test_valid_currency_normalization() -> None:
    c1 = Currency("inr")
    assert c1.code == "INR"
    assert c1.is_supported is True
    assert c1.minor_unit_precision == 2
    assert c1.symbol == "₹"


def test_supported_currency_precision_registry() -> None:
    jpy = Currency("JPY")
    assert jpy.minor_unit_precision == 0

    kwd = Currency("KWD")
    assert kwd.minor_unit_precision == 3

    usd = Currency("USD")
    assert usd.minor_unit_precision == 2


def test_invalid_currency_code_rejected() -> None:
    with pytest.raises(ValidationDomainError):
        Currency("US")

    with pytest.raises(ValidationDomainError):
        Currency("TOOLONG")

    with pytest.raises(ValidationDomainError):
        Currency("123")

    with pytest.raises(ValidationDomainError):
        Currency(None)  # type: ignore[arg-type]


def test_currency_equality_and_immutability() -> None:
    c1 = Currency("INR")
    c2 = Currency("inr")
    assert c1 == c2
    assert hash(c1) == hash(c2)

    with pytest.raises(AttributeError):
        c1.code = "USD"  # type: ignore[misc]
