"""Tenant database model compatibility module (FCD-04 WP-01).

Re-exports canonical Organization entities as Tenant for compatibility.
"""

from menu_it.database.models.organization import (
    Organization as Tenant,
)
from menu_it.database.models.organization import (
    OrganizationStatus as TenantStatus,
)

__all__ = [
    "Tenant",
    "TenantStatus",
]
