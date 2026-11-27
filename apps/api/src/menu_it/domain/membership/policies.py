"""Membership and ownership protection domain policies (FCD-14 WP-01)."""

from uuid import UUID

from menu_it.domain.base.errors import BusinessRuleViolationError


def ensure_not_removing_final_owner(
    *,
    active_owner_count: int,
    target_is_active_owner: bool,
    new_role: str | None = None,
    new_status: str | None = None,
) -> None:
    """Enforce invariant that every active organization must retain at least one active owner."""
    if not target_is_active_owner:
        return
    is_removing_or_demoting = (new_role is not None and new_role != "owner") or (
        new_status is not None and new_status != "active"
    )
    if (
        is_removing_or_demoting or (new_role is None and new_status is None)
    ) and active_owner_count <= 1:
        raise BusinessRuleViolationError(
            "Cannot remove or demote the final active owner of the organization."
        )


def ensure_same_organization_scope(
    expected_organization_id: UUID,
    actual_organization_id: UUID,
    resource_name: str = "resource",
) -> None:
    """Enforce that child/target resources belong to the exact expected organization."""
    if expected_organization_id != actual_organization_id:
        raise BusinessRuleViolationError(
            f"Tenant boundary violation: {resource_name} belongs to another organization."
        )
