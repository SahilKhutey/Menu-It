"""Unit tests for Money value object arithmetic and safety invariants (FCD-06 §7.2, §18.3)."""

from decimal import Decimal

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.currency import Currency
from menu_it.domain.value_objects.money import Money


def test_money_addition() -> None:
    currency = Currency("INR")
    m1 = Money(Decimal("100.25"), currency)
    m2 = Money(Decimal("50.75"), currency)

    res = m1.add(m2)
    assert res.amount == Decimal("151.00")
    assert res.currency == currency


def test_money_subtraction() -> None:
    currency = Currency("INR")
    m1 = Money(Decimal("100.50"), currency)
    m2 = Money(Decimal("40.25"), currency)

    res = m1.subtract(m2)
    assert res.amount == Decimal("60.25")


def test_money_multiplication() -> None:
    m = Money(Decimal("25.50"), Currency("USD"))
    res = m.multiply(Decimal("2"))
    assert res.amount == Decimal("51.00")

    res_int = m.multiply(3)
    assert res_int.amount == Decimal("76.50")

    with pytest.raises(ValidationDomainError):
        m.multiply(2.5)  # type: ignore[arg-type]


def test_money_rejects_currency_mismatch() -> None:
    m1 = Money(Decimal("100"), Currency("INR"))
    m2 = Money(Decimal("100"), Currency("USD"))

    with pytest.raises(ValidationDomainError) as exc:
        m1.add(m2)
    assert "Currency mismatch" in str(exc.value)

    with pytest.raises(ValidationDomainError):
        m1.subtract(m2)


def test_money_rejects_non_decimal_and_non_finite() -> None:
    curr = Currency("INR")

    with pytest.raises(ValidationDomainError):
        Money(100.50, curr)  # type: ignore[arg-type]

    with pytest.raises(ValidationDomainError):
        Money(Decimal("NaN"), curr)

    with pytest.raises(ValidationDomainError):
        Money(Decimal("Infinity"), curr)


def test_money_properties() -> None:
    curr = Currency("INR")
    assert Money(Decimal("0.00"), curr).is_zero is True
    assert Money(Decimal("10.00"), curr).is_positive is True
    assert Money(Decimal("-10.00"), curr).is_negative is True
    assert Money(Decimal("-10.00"), curr).abs().amount == Decimal("10.00")


def test_money_rounding() -> None:
    m_inr = Money(Decimal("10.556"), Currency("INR")).round()
    assert m_inr.amount == Decimal("10.56")

    m_jpy = Money(Decimal("10.556"), Currency("JPY")).round()
    assert m_jpy.amount == Decimal("11")
