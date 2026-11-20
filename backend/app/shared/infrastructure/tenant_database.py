"""
ModularMenu — Tenant Scoped Repository & Database Base (ARC-05 §7, §15.1, ARC05-D08).
Enforces that all repository queries and persistence actions require an authorized tenant scope.
"""
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from app.shared.application.tenant_context import TenantContext
from app.shared.domain.tenant_exceptions import (
    CrossTenantAccessException,
    TenantResourceNotFoundException,
)

T = TypeVar("T")


class TenantScopedRepository(Generic[T]):
    """
    Base repository enforcing organization-scoped queries and entity mutations.
    Guarantees no query can be executed without an explicit, validated tenant scope.
    """
    def __init__(self, entity_store: Optional[dict[UUID, T]] = None):
        self._store: dict[UUID, T] = entity_store if entity_store is not None else {}

    def get_by_id(self, context: TenantContext, entity_id: UUID) -> Optional[T]:
        """Retrieves entity strictly within caller's organization scope."""
        entity = self._store.get(entity_id)
        if entity is None:
            return None
        # Enforce organization ownership
        if getattr(entity, "organization_id", None) != context.organization_id:
            # Conceal existence of cross-tenant resources (prevent enumeration)
            return None
        # Enforce branch scope if entity has restaurant_id and context is branch-restricted
        rest_id = getattr(entity, "restaurant_id", None)
        if rest_id is not None and not context.has_restaurant_access(rest_id):
            return None
        return entity

    def list_all(
        self,
        context: TenantContext,
        restaurant_id: Optional[UUID] = None,
    ) -> List[T]:
        """Lists entities belonging strictly to the authorized tenant."""
        results: List[T] = []
        for entity in self._store.values():
            if getattr(entity, "organization_id", None) != context.organization_id:
                continue
            entity_rest_id = getattr(entity, "restaurant_id", None)
            if restaurant_id and entity_rest_id != restaurant_id:
                continue
            if entity_rest_id and not context.has_restaurant_access(entity_rest_id):
                continue
            results.append(entity)
        return results

    def save(self, context: TenantContext, entity: T) -> T:
        """Saves entity, verifying that its organization_id matches caller's tenant."""
        entity_org_id = getattr(entity, "organization_id", None)
        if entity_org_id != context.organization_id:
            raise CrossTenantAccessException(
                f"Cannot persist entity with organization '{entity_org_id}' "
                f"under context tenant '{context.organization_id}'"
            )
        entity_rest_id = getattr(entity, "restaurant_id", None)
        if entity_rest_id and not context.has_restaurant_access(entity_rest_id):
            raise CrossTenantAccessException(
                f"Context lacks permission to persist entity for branch '{entity_rest_id}'"
            )

        entity_id = getattr(entity, "id", None)
        if entity_id:
            self._store[entity_id] = entity
        return entity

    def delete(self, context: TenantContext, entity_id: UUID) -> bool:
        """Deletes entity strictly within tenant scope."""
        entity = self.get_by_id(context, entity_id)
        if entity is None:
            raise TenantResourceNotFoundException(
                f"Entity '{entity_id}' not found within organization scope"
            )
        del self._store[entity_id]
        return True
