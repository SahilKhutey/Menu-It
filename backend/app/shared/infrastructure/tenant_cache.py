"""
ModularMenu — Tenant-Aware Cache Architecture (ARC-05 §11, ARC05-D14).
Enforces tenant-prefixed cache namespaces and targeted cache invalidation.
"""

from typing import Any
from uuid import UUID

from app.shared.application.tenant_context import TenantContext
from app.shared.domain.tenant_exceptions import CrossTenantAccessException


class TenantCacheManager:
    """
    In-memory and key-prefix cache provider ensuring zero cross-tenant key collisions
    or leakage, regardless of whether Redis or in-process caching is active.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._tenant_keys: dict[UUID, set[str]] = {}

    @staticmethod
    def build_cache_key(
        organization_id: UUID,
        resource: str,
        restaurant_id: UUID | None = None,
        item_id: str | None = None,
    ) -> str:
        """
        Builds a canonical tenant-scoped cache key.
        Format: tenant:{org_id}:restaurant:{restaurant_id}:{resource}:{item_id}
        """
        if restaurant_id and item_id:
            return f"tenant:{organization_id}:restaurant:{restaurant_id}:{resource}:{item_id}"
        elif restaurant_id:
            return f"tenant:{organization_id}:restaurant:{restaurant_id}:{resource}"
        elif item_id:
            return f"tenant:{organization_id}:{resource}:{item_id}"
        return f"tenant:{organization_id}:{resource}"

    def set(
        self,
        context: TenantContext,
        key: str,
        value: Any,
    ) -> None:
        """
        Sets a cache entry. The key MUST be prefixed with the context's organization_id.
        """
        expected_prefix = f"tenant:{context.organization_id}:"
        if not key.startswith(expected_prefix):
            raise CrossTenantAccessException(
                f"Cache write violation: key '{key}' does not match context org '{context.organization_id}'"
            )

        self._store[key] = value
        if context.organization_id not in self._tenant_keys:
            self._tenant_keys[context.organization_id] = set()
        self._tenant_keys[context.organization_id].add(key)

    def get(
        self,
        context: TenantContext,
        key: str,
    ) -> Any | None:
        """
        Retrieves a cache entry, verifying that the requested key belongs to caller's tenant.
        """
        expected_prefix = f"tenant:{context.organization_id}:"
        if not key.startswith(expected_prefix):
            raise CrossTenantAccessException(
                f"Cache read violation: key '{key}' does not match context org '{context.organization_id}'"
            )
        return self._store.get(key)

    def invalidate_tenant(self, organization_id: UUID) -> int:
        """Evicts all cache keys belonging to a specific tenant."""
        keys = self._tenant_keys.pop(organization_id, set())
        for k in keys:
            self._store.pop(k, None)
        return len(keys)

    def invalidate_restaurant(self, organization_id: UUID, restaurant_id: UUID) -> int:
        """Evicts all cache keys for a specific restaurant within a tenant."""
        prefix = f"tenant:{organization_id}:restaurant:{restaurant_id}:"
        keys_to_remove = [
            k for k in self._tenant_keys.get(organization_id, set()) if k.startswith(prefix)
        ]
        for k in keys_to_remove:
            self._store.pop(k, None)
            self._tenant_keys[organization_id].discard(k)
        return len(keys_to_remove)

    def clear_all(self) -> None:
        self._store.clear()
        self._tenant_keys.clear()
