"""
Pricing & Availability Domain Entities (ARC-04 §6.7, MOD-07).
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.shared.domain.value_objects import Money


@dataclass
class Price:
    id: UUID
    item_id: UUID
    amount: Decimal
    currency: str = "INR"
    is_active: bool = True

    def __post_init__(self) -> None:
        # Validate through Money value object
        money = Money(amount=self.amount, currency=self.currency)
        self.amount = money.amount
        self.currency = money.currency

    def change_price(self, new_amount: Decimal) -> None:
        money = Money(amount=new_amount, currency=self.currency)
        self.amount = money.amount


@dataclass
class AvailabilityRule:
    id: UUID
    item_id: UUID
    is_available: bool = True
    reason: str = ""

    def mark_unavailable(self, reason: str = "") -> None:
        self.is_available = False
        self.reason = reason

    def mark_available(self) -> None:
        self.is_available = True
        self.reason = ""
