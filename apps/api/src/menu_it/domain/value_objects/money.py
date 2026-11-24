"""Money value object guaranteeing exact decimal arithmetic and currency safety.

FCD-06 §7.2, §22.1.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.currency import Currency


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary representation enforcing exact Decimal arithmetic and currency safety."""

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise ValidationDomainError("Money amount must be a Decimal instance.")
        if not self.amount.is_finite():
            raise ValidationDomainError("Money amount must be finite.")
        if not isinstance(self.currency, Currency):
            raise ValidationDomainError("Currency must be a Currency value object.")

    def _assert_same_currency(self, other: "Money") -> None:
        if not isinstance(other, Money):
            raise ValidationDomainError("Cannot perform monetary arithmetic with non-Money object.")
        if self.currency != other.currency:
            raise ValidationDomainError(
                f"Currency mismatch: cannot operate between {self.currency.code} "
                f"and {other.currency.code}."
            )

    def add(self, other: "Money") -> "Money":
        """Add two monetary values of identical currency."""
        self._assert_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        """Subtract a monetary value of identical currency."""
        self._assert_same_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: Decimal | int) -> "Money":
        """Multiply amount by a scalar Decimal or integer factor."""
        if isinstance(factor, float):
            raise ValidationDomainError(
                "Multiplication factor must be Decimal or int, never float."
            )
        if isinstance(factor, int):
            factor = Decimal(factor)
        if not isinstance(factor, Decimal) or not factor.is_finite():
            raise ValidationDomainError("Factor must be a finite Decimal.")
        return Money(amount=self.amount * factor, currency=self.currency)

    def round(self, rounding_mode: str = ROUND_HALF_UP) -> "Money":
        """Round amount to the currency's official minor-unit decimal precision."""
        precision = self.currency.minor_unit_precision
        quantize_exp = Decimal(10) ** -precision
        rounded_amount = self.amount.quantize(quantize_exp, rounding=rounding_mode)
        return Money(amount=rounded_amount, currency=self.currency)

    @property
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == Decimal("0")

    @property
    def is_positive(self) -> bool:
        """Check if amount is strictly greater than zero."""
        return self.amount > Decimal("0")

    @property
    def is_negative(self) -> bool:
        """Check if amount is strictly less than zero."""
        return self.amount < Decimal("0")

    def abs(self) -> "Money":
        """Absolute monetary value."""
        return Money(amount=abs(self.amount), currency=self.currency)
