"""
Public Contracts for Menu Module (ARC-04 §8, MOD-04).
"""

from typing import Protocol
from uuid import UUID


class MenuReader(Protocol):
    def menu_exists(self, menu_id: UUID, restaurant_id: UUID) -> bool: ...
