"""
Render Input Domain Entities and Aggregates (ARC-09 §4, WP-ARC09-01).
Strict immutable domain models representing normalized rendering payloads.
Maintains backwards compatibility with ARC-04 §6.11 (MOD-11).
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from app.modules.rendering.domain.render_mode import RenderMode


@dataclass(frozen=True)
class RenderMetadata:
    """Metadata describing the rendered menu package."""
    version_number: int = 1
    checksum: str = ""
    published_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rendered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    renderer_version: str = "1.0.0"
    mode: RenderMode = RenderMode.PUBLIC_PUBLISHED


@dataclass(frozen=True)
class RenderRestaurant:
    """Sanitized restaurant entity for public and preview presentation."""
    id: str = ""
    name: str = ""
    slug: str = ""
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    currency: str = "INR"
    time_zone: str = "Asia/Kolkata"
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


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
    description: Optional[str] = None
    dietary_type: Optional[str] = None
    spice_level: Optional[int] = 0
    image_url: Optional[str] = None
    ingredients: List[str] = field(default_factory=list)
    allergens: List[str] = field(default_factory=list)
    is_available: bool = True
    is_featured: bool = False
    sort_order: int = 0
    badges: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RenderCategory:
    """Presentation category containing ordered food items."""
    id: str = ""
    name: str = ""
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    items: List[RenderItem] = field(default_factory=list)


@dataclass(frozen=True)
class RenderMenu:
    """Presentation menu container."""
    id: str = ""
    name: str = ""
    slug: str = ""
    description: Optional[str] = None
    menu_type: str = "standard"


@dataclass(frozen=True)
class RenderTheme:
    """Resolved theme configuration and CSS token variables."""
    id: str = "preset-classic-slate"
    name: str = "Classic Slate"
    mode: str = "light"
    tokens: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderLayout:
    """Resolved layout configuration."""
    type: str = "category_first"
    card_style: str = "compact"
    columns: int = 1
    density: str = "comfortable"
    show_images: bool = True
    show_descriptions: bool = True
    slots: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderPlan:
    """Deterministic structural composition plan instructing presentation engines."""
    layout_type: str
    slots: Dict[str, str]
    active_components: List[str]
    responsive_breakpoints: Dict[str, str] = field(default_factory=lambda: {
        "mobile": "0px - 639px",
        "tablet": "640px - 1023px",
        "desktop": "1024px+"
    })


@dataclass(frozen=True)
class RenderInput:
    """
    Complete canonical input passed into the presentation engine.
    Compatible with both ARC-04 snapshot dicts and ARC-09 typed aggregates.
    """
    published_snapshot: Optional[Dict[str, Any]] = None
    render_context: Dict[str, Any] = field(default_factory=dict)
    restaurant: Optional[RenderRestaurant] = None
    menu: Optional[RenderMenu] = None
    categories: List[RenderCategory] = field(default_factory=list)
    theme: Optional[RenderTheme] = None
    layout: Optional[RenderLayout] = None
    metadata: Optional[RenderMetadata] = None
    render_mode: RenderMode = RenderMode.PUBLIC_PUBLISHED


@dataclass(frozen=True)
class RenderResult:
    """Canonical output returned from the rendering pipeline."""
    menu_data: Dict[str, Any]
    theme: Dict[str, Any]
    layout: Dict[str, Any]
    components: List[Dict[str, Any]]
    status: str = "success"
    render_plan: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    checksum: Optional[str] = None
    etag: Optional[str] = None
    cache_control: Optional[str] = None
