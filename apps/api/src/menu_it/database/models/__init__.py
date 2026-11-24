"""Database models registry (FCD-03 §9.4)."""

from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)
from menu_it.database.models.tenant import (
    Tenant,
    TenantStatus,
)

__all__ = [
    "Restaurant",
    "RestaurantStatus",
    "Tenant",
    "TenantStatus",
]
