"""Percentage and TaxRate mathematical primitives (FCD-06 §7.3)."""

from dataclasses import dataclass
from decimal import Decimal

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class Percentage:
    """Bounded percentage value between 0 and 100 expressed as a Decimal."""

    value: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.value, float):
            raise ValidationDomainError("Percentage value must be a Decimal, never float.")
        if isinstance(self.value, int):
            object.__setattr__(self, "value", Decimal(self.value))
        if not isinstance(self.value, Decimal) or not self.value.is_finite():
            raise ValidationDomainError("Percentage must be a finite Decimal.")
        if not (Decimal("0") <= self.value <= Decimal("100")):
            raise ValidationDomainError("Percentage must be between 0 and 100.")

    def as_multiplier(self) -> Decimal:
        """Return percentage as a fractional multiplier (e.g. 18% -> 0.18)."""
        return self.value / Decimal("100")


@dataclass(frozen=True, slots=True)
class TaxRate:
    """Tax rate primitive calculating tax on taxable monetary or decimal amounts."""

    percentage: Percentage

    def calculate(self, taxable_amount: Decimal | Money) -> Decimal | Money:
        """Calculate tax portion on a given taxable amount."""
        if isinstance(taxable_amount, Money):
            tax_portion = taxable_amount.amount * self.percentage.as_multiplier()
            return Money(amount=tax_portion, currency=taxable_amount.currency).round()

        if isinstance(taxable_amount, float):
            raise ValidationDomainError("Taxable amount must be Decimal or Money, never float.")
        if not isinstance(taxable_amount, Decimal) or not taxable_amount.is_finite():
            raise ValidationDomainError("Taxable amount must be a finite Decimal.")

        return taxable_amount * self.percentage.as_multiplier()
