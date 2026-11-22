"""
ModularMenu — Seed Reference Data Script (ARC-06 §14, §16 WP-ARC06-01).
Idempotently populates platform-global reference data:
- Built-in visual theme presets (MOD-08)
- Layout presets (MOD-09)
- Component registry definitions (MOD-10)
- Subscription plans (MOD-16)
Guarantees idempotency and never overwrites customer or tenant data.
"""

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.infrastructure.database.models.licensing import SubscriptionPlanModel
from app.infrastructure.database.models.presentation import (
    ComponentDefinitionModel,
    LayoutPresetModel,
    ThemeModel,
)

BUILTIN_THEMES = [
    {
        "theme_key": "modern-minimal",
        "name": "Modern Minimalist",
        "tokens": {
            "color.primary": "#1A1A1A",
            "color.secondary": "#767676",
            "color.background": "#FFFFFF",
            "color.surface": "#F9F9F9",
            "font.heading": "Inter, sans-serif",
            "font.body": "Inter, sans-serif",
            "radius.card": "8px",
        },
    },
    {
        "theme_key": "bold-culinary",
        "name": "Bold Culinary",
        "tokens": {
            "color.primary": "#D9381E",
            "color.secondary": "#2C2C2C",
            "color.background": "#FFFDF9",
            "color.surface": "#F5EFE6",
            "font.heading": "Playfair Display, serif",
            "font.body": "Source Sans Pro, sans-serif",
            "radius.card": "16px",
        },
    },
    {
        "theme_key": "dark-luxe",
        "name": "Dark Luxe",
        "tokens": {
            "color.primary": "#E2B755",
            "color.secondary": "#A3A3A3",
            "color.background": "#121212",
            "color.surface": "#1E1E1E",
            "font.heading": "Cinzel, serif",
            "font.body": "Montserrat, sans-serif",
            "radius.card": "4px",
        },
    },
]

BUILTIN_LAYOUTS = [
    {
        "layout_key": "grid-compact",
        "schema_version": 1,
        "config": {
            "type": "grid",
            "columns": {"mobile": 1, "tablet": 2, "desktop": 3},
            "card_spacing": 16,
        },
    },
    {
        "layout_key": "list-detailed",
        "schema_version": 1,
        "config": {"type": "list", "show_full_description": True, "show_badges": True},
    },
]

BUILTIN_COMPONENTS = [
    {
        "component_key": "header-banner",
        "schema_version": 1,
        "definition": {
            "name": "Header Banner",
            "props": {
                "show_logo": {"type": "boolean", "default": True},
                "show_title": {"type": "boolean", "default": True},
                "show_search": {"type": "boolean", "default": True},
            },
        },
    },
    {
        "component_key": "food-item-card",
        "schema_version": 1,
        "definition": {
            "name": "Food Item Card",
            "props": {
                "show_image": {"type": "boolean", "default": True},
                "show_dietary_badge": {"type": "boolean", "default": True},
                "show_portion_selector": {"type": "boolean", "default": True},
            },
        },
    },
]

BUILTIN_PLANS = [
    {
        "name": "Starter",
        "code": "plan-starter",
        "max_branches": 1,
        "custom_themes_allowed": False,
        "price_minor": 0,
        "currency": "INR",
    },
    {
        "name": "Professional",
        "code": "plan-pro",
        "max_branches": 5,
        "custom_themes_allowed": True,
        "price_minor": 299900,  # 2,999.00 INR
        "currency": "INR",
    },
    {
        "name": "Enterprise",
        "code": "plan-enterprise",
        "max_branches": 50,
        "custom_themes_allowed": True,
        "price_minor": 999900,  # 9,999.00 INR
        "currency": "INR",
    },
]


async def seed_reference_data(session: AsyncSession) -> dict[str, int]:
    """
    Idempotent reference data seeding.
    Inserts missing records without modifying existing tenant or platform data.
    """
    counts = {"themes": 0, "layouts": 0, "components": 0, "plans": 0}

    # 1. Themes
    for t_data in BUILTIN_THEMES:
        stmt = select(ThemeModel).where(ThemeModel.theme_key == t_data["theme_key"])
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            theme = ThemeModel(
                id=uuid.uuid4(),
                owner_organization_id=None,
                name=t_data["name"],
                theme_key=t_data["theme_key"],
                tokens=t_data["tokens"],
                is_system_preset=True,
            )
            session.add(theme)
            counts["themes"] += 1

    # 2. Layouts
    for l_data in BUILTIN_LAYOUTS:
        stmt = select(LayoutPresetModel).where(LayoutPresetModel.layout_key == l_data["layout_key"])
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            layout = LayoutPresetModel(
                id=uuid.uuid4(),
                owner_organization_id=None,
                layout_key=l_data["layout_key"],
                schema_version=l_data["schema_version"],
                config=l_data["config"],
            )
            session.add(layout)
            counts["layouts"] += 1

    # 3. Components
    for c_data in BUILTIN_COMPONENTS:
        stmt = select(ComponentDefinitionModel).where(
            ComponentDefinitionModel.component_key == c_data["component_key"]
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            comp = ComponentDefinitionModel(
                id=uuid.uuid4(),
                component_key=c_data["component_key"],
                schema_version=c_data["schema_version"],
                definition=c_data["definition"],
            )
            session.add(comp)
            counts["components"] += 1

    # 4. Subscription Plans
    for p_data in BUILTIN_PLANS:
        stmt = select(SubscriptionPlanModel).where(SubscriptionPlanModel.code == p_data["code"])
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            plan = SubscriptionPlanModel(
                id=uuid.uuid4(),
                name=p_data["name"],
                code=p_data["code"],
                max_branches=p_data["max_branches"],
                custom_themes_allowed=p_data["custom_themes_allowed"],
                price_minor=p_data["price_minor"],
                currency=p_data["currency"],
            )
            session.add(plan)
            counts["plans"] += 1

    await session.commit()
    return counts


async def main():
    async with AsyncSessionLocal() as session:
        result = await seed_reference_data(session)
        print("Reference data seed result:", result)


if __name__ == "__main__":
    asyncio.run(main())
