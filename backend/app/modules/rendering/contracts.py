"""
Public Contracts for Menu Rendering Module (ARC-04 §8, ARC-09 §4, MOD-11).
"""
from typing import Any, Dict, Protocol, Tuple
from app.modules.rendering.domain.entities import (
    RenderInput,
    RenderResult,
    RenderPlan,
    RenderMode,
)
from app.modules.rendering.schemas.public_render import PublicMenuRenderResponse
from app.modules.rendering.schemas.preview_render import DraftPreviewResponse


class MenuRenderer(Protocol):
    """Core interface for rendering engine."""
    def render(self, data: RenderInput) -> RenderResult:
        ...


class PublicMenuResolver(Protocol):
    """Interface for resolving public published menus."""
    async def resolve_public_menu(
        self,
        restaurant_slug: str,
        menu_slug: str,
    ) -> Tuple[PublicMenuRenderResponse, str, str]:
        ...
