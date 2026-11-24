"""Restaurant lifecycle state definitions and transition rules (FCD-06 §8.4)."""

import enum

from menu_it.domain.base.errors import InvalidStateTransitionError, ValidationDomainError


class RestaurantLifecycleState(enum.StrEnum):
    """Lifecycle states of a restaurant location conforming to FCD-04."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

    @classmethod
    def from_value(cls, val: "RestaurantLifecycleState | str") -> "RestaurantLifecycleState":
        """Normalize value to RestaurantLifecycleState enum."""
        if isinstance(val, RestaurantLifecycleState):
            return val
        if isinstance(val, str):
            clean = val.strip().lower()
            try:
                return cls(clean)
            except ValueError as err:
                raise ValidationDomainError(f"Invalid restaurant lifecycle state: '{val}'") from err
        raise ValidationDomainError(f"Unsupported state type: {type(val)}")


# Explicit state transition graph
ALLOWED_RESTAURANT_TRANSITIONS: dict[RestaurantLifecycleState, set[RestaurantLifecycleState]] = {
    RestaurantLifecycleState.ACTIVE: {
        RestaurantLifecycleState.INACTIVE,
        RestaurantLifecycleState.SUSPENDED,
        RestaurantLifecycleState.ARCHIVED,
    },
    RestaurantLifecycleState.INACTIVE: {
        RestaurantLifecycleState.ACTIVE,
        RestaurantLifecycleState.ARCHIVED,
    },
    RestaurantLifecycleState.SUSPENDED: {
        RestaurantLifecycleState.ACTIVE,
        RestaurantLifecycleState.ARCHIVED,
    },
    RestaurantLifecycleState.ARCHIVED: set(),  # Terminal state
}


def validate_restaurant_transition(
    current_state: RestaurantLifecycleState | str,
    target_state: RestaurantLifecycleState | str,
) -> None:
    """Validate that transition from current_state to target_state is permitted.

    Raises:
        InvalidStateTransitionError: If the transition is prohibited by business rules.
        ValidationDomainError: If either state is not a recognized lifecycle state.
    """
    current = RestaurantLifecycleState.from_value(current_state)
    target = RestaurantLifecycleState.from_value(target_state)

    if current == target:
        return  # No-op transition is permitted

    allowed = ALLOWED_RESTAURANT_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot transition restaurant from '{current.value}' to '{target.value}'."
        )
