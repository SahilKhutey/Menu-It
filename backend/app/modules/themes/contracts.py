"""
Public Contracts for Theme Module (ARC-04 §8, MOD-08).
"""
from typing import Any, Protocol


class ThemeResolver(Protocol):
    def resolve_theme(self, theme_id: str) -> dict[str, Any]:
        ...
