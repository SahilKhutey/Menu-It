"""Restaurant domain module (FCD-06 §8)."""

from menu_it.domain.restaurant.events import (
    RestaurantOperatingHoursUpdated,
    RestaurantProfileUpdated,
    RestaurantStatusChanged,
)
from menu_it.domain.restaurant.lifecycle import (
    ALLOWED_RESTAURANT_TRANSITIONS,
    RestaurantLifecycleState,
    validate_restaurant_transition,
)
from menu_it.domain.restaurant.ownership import assert_restaurant_belongs_to_organization
from menu_it.domain.restaurant.profile import RestaurantProfile
from menu_it.domain.restaurant.references import RestaurantReference

__all__ = [
    "ALLOWED_RESTAURANT_TRANSITIONS",
    "RestaurantLifecycleState",
    "RestaurantOperatingHoursUpdated",
    "RestaurantProfile",
    "RestaurantProfileUpdated",
    "RestaurantReference",
    "RestaurantStatusChanged",
    "assert_restaurant_belongs_to_organization",
    "validate_restaurant_transition",
]
