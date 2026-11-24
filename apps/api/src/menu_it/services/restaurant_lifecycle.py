"""Restaurant lifecycle state machine and transitions (FCD-04 §15)."""

from menu_it.database.models.restaurant import (
    Restaurant,
    RestaurantStatus,
)

ALLOWED_RESTAURANT_TRANSITIONS: dict[RestaurantStatus, set[RestaurantStatus]] = {
    RestaurantStatus.ACTIVE: {
        RestaurantStatus.INACTIVE,
        RestaurantStatus.SUSPENDED,
        RestaurantStatus.ARCHIVED,
    },
    RestaurantStatus.INACTIVE: {
        RestaurantStatus.ACTIVE,
        RestaurantStatus.ARCHIVED,
    },
    RestaurantStatus.SUSPENDED: {
        RestaurantStatus.ACTIVE,
        RestaurantStatus.ARCHIVED,
    },
    RestaurantStatus.ARCHIVED: set(),
}


class InvalidRestaurantTransition(Exception):
    """Raised when an illegal restaurant lifecycle transition is attempted."""

    pass


def transition_restaurant(
    restaurant: Restaurant,
    target: RestaurantStatus,
) -> RestaurantStatus:
    """Validate and apply a restaurant lifecycle state transition."""
    current = restaurant.status
    if current == target:
        return current

    allowed = ALLOWED_RESTAURANT_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidRestaurantTransition(
            f"Cannot transition restaurant from '{current}' to '{target}'."
        )

    restaurant.status = target
    return restaurant.status
