"""Tenancy package exports (FCD-04 §8, §9, §17)."""

from menu_it.tenancy.context import SystemTenantContext, TenantContext
from menu_it.tenancy.contextvar import (
    get_current_tenant,
    reset_current_tenant,
    set_current_tenant,
)
from menu_it.tenancy.exceptions import (
    RestaurantAccessDeniedError,
    TenantAccessDeniedError,
    TenantContextMissingError,
    TenantNotFoundError,
    TenantResolutionError,
    TenantSuspendedError,
)
from menu_it.tenancy.infrastructure import (
    TenantJobContext,
    format_tenant_cache_key,
    format_tenant_storage_key,
    record_audit_event,
)
from menu_it.tenancy.resolver import TenantResolver

__all__ = [
    "RestaurantAccessDeniedError",
    "SystemTenantContext",
    "TenantAccessDeniedError",
    "TenantContext",
    "TenantContextMissingError",
    "TenantJobContext",
    "TenantNotFoundError",
    "TenantResolutionError",
    "TenantResolver",
    "TenantSuspendedError",
    "format_tenant_cache_key",
    "format_tenant_storage_key",
    "get_current_tenant",
    "record_audit_event",
    "reset_current_tenant",
    "set_current_tenant",
]
