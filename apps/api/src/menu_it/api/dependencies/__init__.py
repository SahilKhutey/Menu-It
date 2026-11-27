"""API dependencies package (FCD-07)."""

from menu_it.api.dependencies.authentication import (
    AuthenticatedPrincipal,
    get_authenticated_principal,
    get_current_principal,
)
from menu_it.api.dependencies.pagination import get_pagination_params
from menu_it.api.dependencies.permissions import (
    Permission,
    require_permission,
    require_platform_role,
)
from menu_it.api.dependencies.request_context import get_client_ip, get_request_id
from menu_it.api.dependencies.tenant import (
    TenantContext,
    get_restaurant_tenant_context,
    get_tenant_context,
)

__all__ = [
    "AuthenticatedPrincipal",
    "Permission",
    "TenantContext",
    "get_authenticated_principal",
    "get_client_ip",
    "get_current_principal",
    "get_pagination_params",
    "get_request_id",
    "get_restaurant_tenant_context",
    "get_tenant_context",
    "require_permission",
    "require_platform_role",
]
