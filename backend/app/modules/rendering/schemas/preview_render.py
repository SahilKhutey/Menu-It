"""
Pydantic Schemas for Draft Preview Rendering (ARC-09 §3, WP-ARC09-02).
Conforms strictly to draft-preview-response.schema.json.
Used exclusively by authenticated tenant operators with no-store caching.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.modules.rendering.schemas.public_render import (
    PublicCategoryOut,
    PublicLayoutOut,
    PublicMenuOut,
    PublicRenderPlanOut,
    PublicRestaurantOut,
    PublicThemeOut,
)


class DraftPreviewWarning(BaseModel):
    code: str
    message: str
    field: Optional[str] = None


class DraftPreviewMetadataOut(BaseModel):
    is_preview: bool = True
    draft_version_id: Optional[str] = None
    generated_at: str
    renderer_version: str = "1.0.0"
    watermark_text: str = "PREVIEW - UNPUBLISHED DRAFT"
    warnings: List[DraftPreviewWarning] = Field(default_factory=list)


class DraftPreviewResponse(BaseModel):
    status: str = "preview"
    restaurant: PublicRestaurantOut
    menu: PublicMenuOut
    categories: List[PublicCategoryOut]
    theme: PublicThemeOut
    layout: PublicLayoutOut
    render_plan: PublicRenderPlanOut
    metadata: DraftPreviewMetadataOut
