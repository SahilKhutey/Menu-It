"""
Render Input Domain Entities and Aggregates (ARC-09 §4, WP-ARC09-01).
Strict immutable domain models representing normalized rendering payloads.
Maintains backwards compatibility with ARC-04 §6.11 (MOD-11).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.modules.rendering.domain.render_mode import RenderMode


@dataclass(frozen=True)
class RenderMetadata:
    """Metadata describing the rendered menu package."""

    version_number: int = 1
    checksum: str = ""
    published_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    rendered_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    renderer_version: str = "1.0.0"
    mode: RenderMode = RenderMode.PUBLIC_PUBLISHED


@dataclass(frozen=True)
class RenderRestaurant:
    """Sanitized restaurant entity for public and preview presentation."""

    id: str = ""
    name: str = ""
    slug: str = ""
    description: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    currency: str = "INR"
    time_zone: str = "Asia/Kolkata"
    phone: str | None = None
    email: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class RenderPrice:
    """Monetary presentation model with decimal precision and formatted currency."""

    amount: Decimal = Decimal("0.00")
    currency: str = "INR"
    formatted: str = ""

    def __post_init__(self):
        if self.amount < Decimal("0.00"):
            raise ValueError(f"Price amount cannot be negative: {self.amount}")


@dataclass(frozen=True)
class RenderItem:
    """Presentation item with formatted pricing, dietary classifications, and media."""

    id: str = ""
    name: str = ""
    price: Decimal = Decimal("0.00")
    formatted_price: str = ""
    currency_code: str = "INR"
    description: str | None = None
    dietary_type: str | None = None
    spice_level: int | None = 0
    image_url: str | None = None
    ingredients: list[str] = field(default_factory=list)
    allergens: list[str] = field(default_factory=list)
    is_available: bool = True
    is_featured: bool = False
    sort_order: int = 0
    badges: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RenderCategory:
    """Presentation category containing ordered food items."""

    id: str = ""
    name: str = ""
    description: str | None = None
    image_url: str | None = None
    sort_order: int = 0
    items: list[RenderItem] = field(default_factory=list)


@dataclass(frozen=True)
class RenderMenu:
    """Presentation menu container."""

    id: str = ""
    name: str = ""
    slug: str = ""
    description: str | None = None
    menu_type: str = "standard"


@dataclass(frozen=True)
class RenderTheme:
    """Resolved theme configuration and CSS token variables."""

    id: str = "preset-classic-slate"
    name: str = "Classic Slate"
    mode: str = "light"
    tokens: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderLayout:
    """Resolved layout configuration."""

    type: str = "category_first"
    card_style: str = "compact"
    columns: int = 1
    density: str = "comfortable"
    show_images: bool = True
    show_descriptions: bool = True
    slots: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderPlan:
    """Deterministic structural composition plan instructing presentation engines."""

    layout_type: str
    slots: dict[str, str]
    active_components: list[str]
    responsive_breakpoints: dict[str, str] = field(
        default_factory=lambda: {
            "mobile": "0px - 639px",
            "tablet": "640px - 1023px",
            "desktop": "1024px+",
        }
    )


@dataclass(frozen=True)
class RenderInput:
    """
    Complete canonical input passed into the presentation engine.
    Compatible with both ARC-04 snapshot dicts and ARC-09 typed aggregates.
    """

    published_snapshot: dict[str, Any] | None = None
    render_context: dict[str, Any] = field(default_factory=dict)
    restaurant: RenderRestaurant | None = None
    menu: RenderMenu | None = None
    categories: list[RenderCategory] = field(default_factory=list)
    theme: RenderTheme | None = None
    layout: RenderLayout | None = None
    metadata: RenderMetadata | None = None
    render_mode: RenderMode = RenderMode.PUBLIC_PUBLISHED


@dataclass(frozen=True)
class RenderResult:
    """Canonical output returned from the rendering pipeline."""

    menu_data: dict[str, Any]
    theme: dict[str, Any]
    layout: dict[str, Any]
    components: list[dict[str, Any]]
    status: str = "success"
    render_plan: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    checksum: str | None = None
    etag: str | None = None
    cache_control: str | None = None
