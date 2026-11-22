"""
Render Input Builder Service (ARC-09 §4, WP-ARC09-01).
Constructs canonical RenderInput and RenderPlan models from raw snapshots or draft models.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.modules.rendering.domain.render_input import (
    RenderCategory,
    RenderInput,
    RenderItem,
    RenderLayout,
    RenderMenu,
    RenderMetadata,
    RenderPlan,
    RenderRestaurant,
    RenderTheme,
)
from app.modules.rendering.domain.render_mode import RenderMode


class RenderInputBuilder:
    """Transforms raw snapshot dictionaries or live database objects into canonical RenderInput."""

    @staticmethod
    def format_price(amount: Decimal, currency_code: str = "INR") -> str:
        """Formats monetary amount according to currency standards."""
        if currency_code.upper() == "INR":
            return f"₹{amount:,.2f}".rstrip("0").rstrip(".") if amount % 1 == 0 else f"₹{amount:,.2f}"
        elif currency_code.upper() == "USD":
            return f"${amount:,.2f}"
        elif currency_code.upper() == "EUR":
            return f"€{amount:,.2f}"
        elif currency_code.upper() == "GBP":
            return f"£{amount:,.2f}"
        return f"{currency_code.upper()} {amount:,.2f}"

    @classmethod
    def build_from_snapshot(
        cls,
        snapshot_data: Dict[str, Any],
        version_number: int,
        checksum: str,
        published_at: str,
        render_mode: RenderMode = RenderMode.PUBLIC_PUBLISHED,
    ) -> RenderInput:
        """Constructs canonical RenderInput from an immutable published snapshot."""
        # Restaurant
        rest_raw = snapshot_data.get("restaurant", {})
        restaurant = RenderRestaurant(
            id=str(rest_raw.get("id", "")),
            name=rest_raw.get("name", "Restaurant"),
            slug=rest_raw.get("slug", ""),
            description=rest_raw.get("description"),
            logo_url=rest_raw.get("logo_url"),
            cover_url=rest_raw.get("cover_url"),
            currency=rest_raw.get("currency", "INR"),
            time_zone=rest_raw.get("time_zone", "Asia/Kolkata"),
            phone=rest_raw.get("phone"),
            email=rest_raw.get("email"),
            address=rest_raw.get("address"),
        )

        # Menu
        menu_raw = snapshot_data.get("menu", {})
        menu = RenderMenu(
            id=str(menu_raw.get("id", "")),
            name=menu_raw.get("name", "Menu"),
            slug=menu_raw.get("slug", ""),
            description=menu_raw.get("description"),
            menu_type=menu_raw.get("menu_type", "standard"),
        )

        # Categories & Items
        categories: List[RenderCategory] = []
        for cat_raw in snapshot_data.get("categories", []):
            items: List[RenderItem] = []
            for item_raw in cat_raw.get("items", []):
                base_price = Decimal(str(item_raw.get("base_price", item_raw.get("price", 0))))
                currency_code = item_raw.get("currency_code", restaurant.currency)
                formatted_price = cls.format_price(base_price, currency_code)

                # Badges derivation
                badges: List[str] = list(item_raw.get("badges", []))
                dietary = item_raw.get("dietary_type")
                if dietary and dietary.capitalize() not in badges:
                    badges.append(dietary.capitalize())
                if item_raw.get("is_featured") and "Featured" not in badges:
                    badges.append("Featured")
                spice_raw = item_raw.get("spice_level", 0)
                spice_int = 0
                if isinstance(spice_raw, int):
                    spice_int = spice_raw
                elif isinstance(spice_raw, str):
                    spice_map = {"none": 0, "mild": 1, "medium": 2, "hot": 3, "extra_hot": 4}
                    spice_int = spice_map.get(spice_raw.lower(), 1 if spice_raw else 0)

                if spice_int > 0 and f"Spicy {spice_int}/3" not in badges:
                    badges.append(f"Spicy {spice_int}/3")

                items.append(
                    RenderItem(
                        id=str(item_raw.get("id", "")),
                        name=item_raw.get("name", ""),
                        price=base_price,
                        formatted_price=formatted_price,
                        currency_code=currency_code,
                        description=item_raw.get("description"),
                        dietary_type=dietary,
                        spice_level=spice_int,
                        image_url=item_raw.get("image_url"),
                        ingredients=item_raw.get("ingredients", []),
                        allergens=item_raw.get("allergens", []),
                        is_available=item_raw.get("is_available", True),
                        is_featured=item_raw.get("is_featured", False),
                        sort_order=int(item_raw.get("sort_order", 0)),
                        badges=badges,
                    )
                )

            # Sort items by sort_order
            items.sort(key=lambda x: x.sort_order)

            categories.append(
                RenderCategory(
                    id=str(cat_raw.get("id", "")),
                    name=cat_raw.get("name", ""),
                    description=cat_raw.get("description"),
                    image_url=cat_raw.get("image_url"),
                    sort_order=int(cat_raw.get("sort_order", 0)),
                    items=items,
                )
            )

        # Sort categories by sort_order
        categories.sort(key=lambda x: x.sort_order)

        # Theme
        theme_raw = snapshot_data.get("theme", {})
        tokens = theme_raw.get("tokens", theme_raw) if isinstance(theme_raw, dict) else {}
        theme = RenderTheme(
            id=theme_raw.get("id", "preset-classic-slate") if isinstance(theme_raw, dict) else "preset-classic-slate",
            name=theme_raw.get("name", "Classic Slate") if isinstance(theme_raw, dict) else "Classic Slate",
            mode=theme_raw.get("mode", "light") if isinstance(theme_raw, dict) else "light",
            tokens=tokens,
        )

        # Layout
        layout_raw = snapshot_data.get("layout", {})
        default_slots = {
            "header": "RestaurantHeroHeader",
            "navigation": "CategoryPillNav",
            "category_section": "CategorySection",
            "item_card": "FoodItemCard",
            "footer": "MenuFooter",
        }
        slots = {**default_slots, **layout_raw.get("slots", {})}
        layout = RenderLayout(
            type=layout_raw.get("type", "category_first"),
            card_style=layout_raw.get("card_style", "compact"),
            columns=int(layout_raw.get("columns", 1)),
            density=layout_raw.get("density", "comfortable"),
            show_images=layout_raw.get("show_images", True),
            show_descriptions=layout_raw.get("show_descriptions", True),
            slots=slots,
        )

        # Metadata
        metadata = RenderMetadata(
            version_number=version_number,
            checksum=checksum,
            published_at=published_at,
            mode=render_mode,
        )

        return RenderInput(
            restaurant=restaurant,
            menu=menu,
            categories=categories,
            theme=theme,
            layout=layout,
            metadata=metadata,
            render_mode=render_mode,
        )

    @staticmethod
    def build_render_plan(layout: RenderLayout) -> RenderPlan:
        """Constructs a deterministic RenderPlan from layout slots and rules."""
        active_components = list(set(layout.slots.values()))
        active_components.sort()
        return RenderPlan(
            layout_type=layout.type,
            slots=layout.slots,
            active_components=active_components,
        )
