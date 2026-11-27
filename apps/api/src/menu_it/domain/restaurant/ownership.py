"""Tenant ownership validation invariants for restaurant resources (FCD-06 §8.3)."""

from uuid import UUID

from menu_it.domain.base.errors import BusinessRuleViolationError


def assert_restaurant_belongs_to_organization(
    restaurant_org_id: UUID,
    context_org_id: UUID,
) -> None:
    """Validate that restaurant's owning organization matches tenant context.

    Invariant:
    Resource.organization_id == Restaurant.organization_id == Owning Organization.id
    """
    if restaurant_org_id != context_org_id:
        raise BusinessRuleViolationError(
            f"Tenant ownership mismatch: restaurant belongs to organization '{restaurant_org_id}', "
            f"not authorized tenant '{context_org_id}'."
        )
