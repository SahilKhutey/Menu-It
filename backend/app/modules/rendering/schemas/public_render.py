"""
Pydantic Schemas for Public Menu Rendering (ARC-09 §4, WP-ARC09-01).
Conforms strictly to public-menu-response.schema.json.
Guarantees zero internal metadata, tenant keys, or draft properties leak.
"""

from typing import Any

from pydantic import BaseModel, Field


class PublicRestaurantOut(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    currency: str = "INR"
    time_zone: str = "Asia/Kolkata"
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class PublicItemOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    price: float
    formatted_price: str
    currency_code: str = "INR"
    dietary_type: str | None = None
    spice_level: int | None = 0
    image_url: str | None = None
    ingredients: list[str] = Field(default_factory=list)
    allergens: list[str] = Field(default_factory=list)
    is_available: bool = True
    is_featured: bool = False
    sort_order: int = 0
    badges: list[str] = Field(default_factory=list)


class PublicCategoryOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    image_url: str | None = None
    sort_order: int = 0
    items: list[PublicItemOut] = Field(default_factory=list)


class PublicMenuOut(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None = None
    menu_type: str = "standard"


class PublicThemeOut(BaseModel):
    id: str
    name: str
    mode: str = "light"
    tokens: dict[str, Any] = Field(default_factory=dict)


class PublicLayoutOut(BaseModel):
    type: str = "category_first"
    card_style: str = "compact"
    columns: int = 1
    density: str = "comfortable"
    show_images: bool = True
    show_descriptions: bool = True
    slots: dict[str, str] = Field(default_factory=dict)


class PublicRenderPlanOut(BaseModel):
    layout_type: str
    slots: dict[str, str]
    active_components: list[str]
    responsive_breakpoints: dict[str, str] = Field(
        default_factory=lambda: {
            "mobile": "0px - 639px",
            "tablet": "640px - 1023px",
            "desktop": "1024px+",
        }
    )


class PublicMetadataOut(BaseModel):
    version_number: int
    checksum: str
    published_at: str
    rendered_at: str
    renderer_version: str = "1.0.0"


class PublicMenuRenderResponse(BaseModel):
    status: str = "success"
    restaurant: PublicRestaurantOut
    menu: PublicMenuOut
    categories: list[PublicCategoryOut]
    theme: PublicThemeOut
    layout: PublicLayoutOut
    render_plan: PublicRenderPlanOut
    metadata: PublicMetadataOut
