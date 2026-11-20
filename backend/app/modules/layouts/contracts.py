"""
Public Contracts for Layout Module (ARC-04 §8, MOD-09).
"""
from typing import Protocol
from app.modules.layouts.domain.entities import LayoutDefinition


class LayoutResolver(Protocol):
    def get_layout(self, layout_id: str) -> LayoutDefinition | None:
        ...
