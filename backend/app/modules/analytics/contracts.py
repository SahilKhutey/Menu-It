"""
Public Contracts for Analytics Module (ARC-04 §8, MOD-16).
"""
from typing import Protocol
from uuid import UUID


class AnalyticsRecorder(Protocol):
    def record_page_view(self, restaurant_id: UUID) -> None:
        ...
