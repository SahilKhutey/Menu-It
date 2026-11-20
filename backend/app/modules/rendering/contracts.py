"""
Public Contracts for Menu Rendering Module (ARC-04 §8, MOD-11).
"""
from typing import Protocol
from app.modules.rendering.domain.entities import RenderInput, RenderResult


class MenuRenderer(Protocol):
    def render(self, data: RenderInput) -> RenderResult:
        ...
