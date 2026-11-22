"""
Public Contracts for Restaurant Module (ARC-04 §8, MOD-03).
"""

from typing import Protocol
from uuid import UUID


class RestaurantReader(Protocol):
    def restaurant_exists(self, restaurant_id: UUID) -> bool: ...

    def is_restaurant_active(self, restaurant_id: UUID) -> bool: ...
