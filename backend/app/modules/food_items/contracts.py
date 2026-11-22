"""
Public Contracts for Food Items Module (ARC-04 §8, MOD-06).
"""

from typing import Protocol
from uuid import UUID


class FoodItemReader(Protocol):
    def item_exists(self, item_id: UUID) -> bool: ...
