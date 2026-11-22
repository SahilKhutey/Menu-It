"""
Public Contracts for Pricing Module (ARC-04 §8, MOD-07).
"""

from typing import Protocol
from uuid import UUID

from app.shared.domain.value_objects import Money


class PricingReader(Protocol):
    def get_item_price(self, item_id: UUID) -> Money | None: ...
