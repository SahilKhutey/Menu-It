"""
Public Contracts for Visual Menu Editor (ARC-04 §8, MOD-12).
"""

from typing import Any, Protocol
from uuid import UUID


class EditorDraftManager(Protocol):
    def get_draft_configuration(self, restaurant_id: UUID) -> dict[str, Any] | None: ...
