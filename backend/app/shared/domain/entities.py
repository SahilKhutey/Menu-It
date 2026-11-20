"""
Pure Domain Entities (ARC-03 §4.5 & §5).
These are domain models with business invariants, completely free of ORM and HTTP dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import uuid
from typing import Optional
from app.shared.domain.exceptions import BusinessRuleViolationException


SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class MenuEntity:
    """Menu Aggregate Root representing an active or draft restaurant menu."""
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    slug: str
    menu_type: str = "all_day"
    description: Optional[str] = None
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Enforces domain invariants for menu aggregates."""
        if not self.name or len(self.name.strip()) < 2:
            raise BusinessRuleViolationException(
                "MenuNameRequired",
                "Menu name must be at least 2 characters long."
            )
        if len(self.name) > 100:
            raise BusinessRuleViolationException(
                "MenuNameTooLong",
                "Menu name cannot exceed 100 characters."
            )
        if not self.slug or not SLUG_REGEX.match(self.slug):
            raise BusinessRuleViolationException(
                "InvalidSlugFormat",
                f"Slug '{self.slug}' does not match required kebab-case format."
            )
        if not self.restaurant_id:
            raise BusinessRuleViolationException(
                "TenantRequired",
                "Menu must belong to a valid restaurant tenant."
            )

    def rename(self, new_name: str):
        """Domain method to update name with invariant enforcement."""
        self.name = new_name
        self.validate()
