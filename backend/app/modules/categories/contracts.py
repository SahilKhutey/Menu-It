"""
Public Contracts for Category Module (ARC-04 §8, MOD-05).
"""

from typing import Protocol
from uuid import UUID


class CategoryReader(Protocol):
    def category_exists(self, category_id: UUID, menu_id: UUID) -> bool: ...
