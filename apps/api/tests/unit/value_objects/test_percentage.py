"""Unit tests for Percentage and TaxRate primitives (FCD-06 §7.3)."""

from decimal import Decimal

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.money import Money
from menu_it.domain.value_objects.percentage import Percentage, TaxRate


def test_percentage_valid_and_multiplier() -> None:
    p = Percentage(Decimal("18"))
    assert p.value == Decimal("18")
    assert p.as_multiplier() == Decimal("0.18")

    p_zero = Percentage(0)
    assert p_zero.as_multiplier() == Decimal("0")

    p_hundred = Percentage(100)
    assert p_hundred.as_multiplier() == Decimal("1")


def test_percentage_invalid_range_and_types() -> None:
    with pytest.raises(ValidationDomainError):
        Percentage(Decimal("-1"))

    with pytest.raises(ValidationDomainError):
        Percentage(Decimal("100.1"))

    with pytest.raises(ValidationDomainError):
        Percentage(18.5)  # type: ignore[arg-type]


def test_tax_rate_calculation_on_decimal_and_money() -> None:
    gst = TaxRate(Percentage(Decimal("18")))

    tax_dec = gst.calculate(Decimal("1000.00"))
    assert tax_dec == Decimal("180.00")

    tax_money = gst.calculate(Money(Decimal("1000.00"), Currency("INR")))
    assert isinstance(tax_money, Money)
    assert tax_money.amount == Decimal("180.00")
    assert tax_money.currency.code == "INR"
