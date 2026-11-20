"""
Restaurant Domain Entities (ARC-04 §6.3, MOD-03).
"""
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID
from app.shared.domain.value_objects import RestaurantSlug


@dataclass
class RestaurantSettings:
    currency: str = "INR"
    locale: str = "en-IN"
    timezone: str = "Asia/Kolkata"
    enable_dietary_indicators: bool = True
    enable_allergens: bool = True

    def validate_schema(self) -> None:
        if len(self.currency) != 3 or not self.currency.isupper():
            raise ValueError("Invalid currency code in settings")
        if not self.timezone:
            raise ValueError("Timezone cannot be empty")


@dataclass
class Restaurant:
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    is_active: bool = True
    settings: RestaurantSettings = field(default_factory=RestaurantSettings)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Restaurant name is required")
        if not self.organization_id:
            raise ValueError("A restaurant must belong to an organization")
        # Validate slug invariant
        self.slug = RestaurantSlug(self.slug).value
        self.settings.validate_schema()

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def update_settings(self, new_settings: RestaurantSettings) -> None:
        new_settings.validate_schema()
        self.settings = new_settings
