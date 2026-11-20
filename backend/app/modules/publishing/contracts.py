"""
Public Contracts for Publishing Module (ARC-04 §8, MOD-13).
"""
from typing import Any, Protocol
from uuid import UUID


class PublishedSnapshotReader(Protocol):
    def get_active_snapshot(self, menu_id: UUID) -> dict[str, Any] | None:
        ...
