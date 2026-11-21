import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, verify_restaurant_access
from app.modules.identity.models import Restaurant
from app.modules.themes.models import RestaurantDesignConfig, Theme
from app.modules.themes.presets import THEME_PRESETS

router = APIRouter(tags=["Themes & Design"])


class DesignConfigUpdate(BaseModel):
    theme_key: str
    layout_config: Dict[str, Any] = {}
    custom_tokens: Dict[str, Any] = {}


@router.get("/themes", response_model=List[Dict[str, Any]])
async def list_available_themes(db: AsyncSession = Depends(get_db)):
    # Return pre-defined system presets
    return THEME_PRESETS


@router.get("/restaurants/{restaurant_id}/design")
async def get_restaurant_design(
    restaurant_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(RestaurantDesignConfig).where(RestaurantDesignConfig.restaurant_id == restaurant.id)
    result = await db.execute(stmt)
    config = result.scalars().first()

    if not config:
        # Default to 'contemporary' preset
        default_preset = next((p for p in THEME_PRESETS if p["theme_key"] == "contemporary"), THEME_PRESETS[0])
        return {
            "restaurant_id": restaurant.id,
            "theme_key": default_preset["theme_key"],
            "tokens": default_preset["tokens"],
            "layout_config": {"type": "category_first", "card_style": "compact"},
            "custom_tokens": {}
        }

    # Fetch theme details
    theme_stmt = select(Theme).where(Theme.id == config.theme_id)
    theme_res = await db.execute(theme_stmt)
    theme = theme_res.scalars().first()
    theme_key = theme.theme_key if theme else "contemporary"
    base_tokens = theme.tokens if theme else THEME_PRESETS[0]["tokens"]

    return {
        "restaurant_id": restaurant.id,
        "theme_key": theme_key,
        "tokens": {**base_tokens, **config.custom_tokens},
        "layout_config": config.layout_config,
        "custom_tokens": config.custom_tokens
    }


@router.put("/restaurants/{restaurant_id}/design")
async def update_restaurant_design(
    restaurant_id: uuid.UUID,
    req: DesignConfigUpdate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
):
    # Find matching theme in DB or preset
    preset = next((p for p in THEME_PRESETS if p["theme_key"] == req.theme_key), None)
    if not preset:
        raise HTTPException(status_code=400, detail=f"Unknown theme preset: {req.theme_key}")

    # Ensure theme exists in DB
    theme_stmt = select(Theme).where(Theme.theme_key == req.theme_key)
    theme_res = await db.execute(theme_stmt)
    theme = theme_res.scalars().first()
    if not theme:
        theme = Theme(
            name=preset["name"],
            theme_key=preset["theme_key"],
            tokens=preset["tokens"],
            is_system_preset=True
        )
        db.add(theme)
        await db.flush()

    cfg_stmt = select(RestaurantDesignConfig).where(RestaurantDesignConfig.restaurant_id == restaurant.id)
    cfg_res = await db.execute(cfg_stmt)
    config = cfg_res.scalars().first()

    if not config:
        config = RestaurantDesignConfig(
            restaurant_id=restaurant.id,
            theme_id=theme.id,
            layout_config=req.layout_config,
            custom_tokens=req.custom_tokens
        )
        db.add(config)
    else:
        config.theme_id = theme.id
        config.layout_config = req.layout_config
        config.custom_tokens = req.custom_tokens
        config.config_version += 1

    await db.commit()
    return {"status": "success", "message": "Design configuration updated"}


@router.get("/layouts")
async def list_supported_layouts():
    """Lists supported layout presets (ARC-07 §4.6)."""
    return [
        {"id": str(uuid.UUID("22222222-0000-0000-0000-000000000001")), "name": "Grid", "slug": "grid", "supported_slots": ["header", "categories", "grid_items", "footer"], "is_system_preset": True},
        {"id": str(uuid.UUID("22222222-0000-0000-0000-000000000002")), "name": "List", "slug": "list", "supported_slots": ["header", "categories", "list_items", "footer"], "is_system_preset": True},
        {"id": str(uuid.UUID("22222222-0000-0000-0000-000000000003")), "name": "Cards", "slug": "cards", "supported_slots": ["header", "hero", "card_items", "footer"], "is_system_preset": True},
        {"id": str(uuid.UUID("22222222-0000-0000-0000-000000000004")), "name": "Magazine", "slug": "magazine", "supported_slots": ["header", "feature", "editorial_items", "footer"], "is_system_preset": True},
    ]


@router.get("/components")
async def list_registered_components():
    """Lists whitelisted UI components from the component registry (ARC-07 §4.6)."""
    return [
        {"id": str(uuid.UUID("33333333-0000-0000-0000-000000000001")), "component_key": "hero_banner", "name": "Hero Banner", "category": "header", "props_schema": {}, "is_deprecated": False},
        {"id": str(uuid.UUID("33333333-0000-0000-0000-000000000002")), "component_key": "category_nav", "name": "Category Navigation", "category": "navigation", "props_schema": {}, "is_deprecated": False},
        {"id": str(uuid.UUID("33333333-0000-0000-0000-000000000003")), "component_key": "food_card", "name": "Food Card", "category": "items", "props_schema": {}, "is_deprecated": False},
        {"id": str(uuid.UUID("33333333-0000-0000-0000-000000000004")), "component_key": "dietary_badges", "name": "Dietary Badges", "category": "badges", "props_schema": {}, "is_deprecated": False},
    ]

