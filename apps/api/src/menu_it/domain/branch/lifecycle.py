"""Branch lifecycle state definitions and transition rules (FCD-14 WP-01)."""

import enum

from menu_it.domain.base.errors import InvalidStateTransitionError, ValidationDomainError


class BranchLifecycleState(enum.StrEnum):
    """Lifecycle states of a physical restaurant branch."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

    @classmethod
    def from_value(cls, val: "BranchLifecycleState | str") -> "BranchLifecycleState":
        """Normalize string or enum to BranchLifecycleState."""
        if isinstance(val, BranchLifecycleState):
            return val
        if isinstance(val, str):
            clean = val.strip().lower()
            try:
                return cls(clean)
            except ValueError as err:
                raise ValidationDomainError(f"Invalid branch lifecycle state: '{val}'") from err
        raise ValidationDomainError(f"Unsupported state type: {type(val)}")


ALLOWED_BRANCH_TRANSITIONS: dict[BranchLifecycleState, set[BranchLifecycleState]] = {
    BranchLifecycleState.ACTIVE: {
        BranchLifecycleState.INACTIVE,
        BranchLifecycleState.SUSPENDED,
        BranchLifecycleState.ARCHIVED,
    },
    BranchLifecycleState.INACTIVE: {
        BranchLifecycleState.ACTIVE,
        BranchLifecycleState.ARCHIVED,
    },
    BranchLifecycleState.SUSPENDED: {
        BranchLifecycleState.ACTIVE,
        BranchLifecycleState.ARCHIVED,
    },
    BranchLifecycleState.ARCHIVED: set(),
}


def validate_branch_transition(
    current_state: BranchLifecycleState | str,
    target_state: BranchLifecycleState | str,
) -> None:
    """Validate that a branch lifecycle transition is permitted."""
    current = BranchLifecycleState.from_value(current_state)
    target = BranchLifecycleState.from_value(target_state)

    if current == target:
        return

    allowed = ALLOWED_BRANCH_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot transition branch from '{current.value}' to '{target.value}'."
        )
