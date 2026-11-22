"""
Pure Domain Value Objects (ARC-04 §7.2, WP-ARC04-03).
Independent of frameworks, databases, and HTTP layers.
"""

import re
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """
    Validated monetary value object.
    Enforces non-negative finite Decimal and 3-letter ISO-4217 currency code.
    """

    amount: Decimal
    currency: str = "INR"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise ValueError("Price amount must be a Decimal instance")
        if not self.amount.is_finite() or self.amount < Decimal("0"):
            raise ValueError("Price must be a finite non-negative amount")
        normalized_currency = self.currency.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", normalized_currency):
            raise ValueError("Currency must be a 3-letter ISO code")
        object.__setattr__(self, "currency", normalized_currency)


@dataclass(frozen=True)
class EmailAddress:
    """
    Validated and normalized email address value object.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if len(normalized) > 254:
            raise ValueError("Email address is too long (max 254 characters)")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Invalid email address syntax")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class RestaurantSlug:
    """
    Validated URL-safe slug for restaurant identifiers.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not re.fullmatch(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", normalized):
            raise ValueError(f"Invalid restaurant slug format: '{self.value}'")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class MenuSlug:
    """
    Validated URL-safe slug for menu identifiers.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not re.fullmatch(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", normalized):
            raise ValueError(f"Invalid menu slug format: '{self.value}'")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class DisplayOrder:
    """
    Deterministic zero-indexed ordering value object.
    """

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Display order must be a non-negative integer")
