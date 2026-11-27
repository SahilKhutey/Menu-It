"""Authorization and tenant boundary assertion helpers (FCD-11 WP-03 / WP-04)."""

from collections.abc import Iterable
from uuid import UUID


class TenantAccessDeniedError(Exception):
    """Raised when an actor attempts to access a resource belonging to a different tenant."""

    def __init__(
        self,
        resource_org_id: UUID | None,
        context_org_id: UUID | None,
        message: str | None = None,
    ) -> None:
        self.resource_org_id = resource_org_id
        self.context_org_id = context_org_id
        default_msg = (
            f"Tenant boundary violation: Context organization '{context_org_id}' "
            f"cannot access resource of organization '{resource_org_id}'."
        )
        super().__init__(message or default_msg)


class PermissionDeniedError(Exception):
    """Raised when an actor lacks the required permission for an operation."""

    def __init__(self, required_permission: str, available_permissions: Iterable[str]) -> None:
        self.required_permission = required_permission
        self.available_permissions = set(available_permissions)
        super().__init__(f"Permission denied: Missing required permission '{required_permission}'.")


def assert_tenant_boundary(
    resource_org_id: UUID | None,
    context_org_id: UUID | None,
    *,
    allow_unscoped_resource: bool = False,
) -> None:
    """Assert that the target resource belongs to the current tenant context.

    Raises:
        TenantAccessDeniedError: If context_org_id does not match resource_org_id.
    """
    if resource_org_id is None and allow_unscoped_resource:
        return

    if resource_org_id != context_org_id:
        raise TenantAccessDeniedError(
            resource_org_id=resource_org_id,
            context_org_id=context_org_id,
        )


def require_permission(
    available_permissions: Iterable[str],
    required_permission: str,
) -> None:
    """Verify that the required permission is present in the actor's permissions set.

    Supports wildcard '*' or 'admin' for superuser permissions.

    Raises:
        PermissionDeniedError: If the permission is not satisfied.
    """
    perms = set(available_permissions)
    if "*" in perms or "admin" in perms or required_permission in perms:
        return

    # Check for domain wildcard (e.g. 'restaurant:*' grants 'restaurant:read')
    if ":" in required_permission:
        domain = required_permission.split(":", 1)[0]
        if f"{domain}:*" in perms:
            return

    raise PermissionDeniedError(required_permission, perms)
