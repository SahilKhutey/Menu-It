"""Tenant-aware cache key generation and namespace isolation (FCD-10 WP-02)."""

from uuid import UUID


def organization_key(
    organization_id: UUID,
    resource: str,
    identifier: str,
) -> str:
    """Generate tenant-isolated private cache key.

    Pattern: menu-it:v1:org:{organization_id}:{resource}:{identifier}
    """
    if not resource or ":" in resource:
        raise ValueError("Invalid resource namespace: must be non-empty and cannot contain ':'.")
    if not identifier or ":" in identifier:
        raise ValueError("Invalid resource identifier: must be non-empty and cannot contain ':'.")
    return f"menu-it:v1:org:{organization_id}:{resource}:{identifier}"


def public_key(resource: str, identifier: str) -> str:
    """Generate public unauthenticated cache key (e.g. public menus, slugs).

    Pattern: menu-it:v1:public:{resource}:{identifier}
    """
    if not resource or ":" in resource:
        raise ValueError("Invalid resource namespace: must be non-empty and cannot contain ':'.")
    if not identifier or ":" in identifier:
        raise ValueError("Invalid resource identifier: must be non-empty and cannot contain ':'.")
    return f"menu-it:v1:public:{resource}:{identifier}"
