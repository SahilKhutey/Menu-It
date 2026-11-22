import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
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
    layout_config: dict[str, Any] = {}
    custom_tokens: dict[str, Any] = {}


@router.get("/themes", response_model=list[dict[str, Any]])
async def list_available_themes(db: AsyncSession = Depends(get_db)):
    """Lists platform theme presets (ARC-08 §6)."""
    from app.modules.customization.registries import theme_registry

    catalogue = theme_registry.list_all()
    if catalogue:
        for t in catalogue:
            t["theme_key"] = t.get("slug", t["id"])
        return catalogue
    return THEME_PRESETS


@router.get("/themes/{theme_id}")
async def get_theme_definition(theme_id: str):
    """Retrieves theme preset definition by ID or slug."""
    from app.modules.customization.registries import theme_registry

    theme = theme_registry.get(theme_id)
    if not theme and not theme_id.startswith("theme-"):
        theme = theme_registry.get(f"theme-{theme_id}")
    if not theme:
        raise HTTPException(status_code=404, detail=f"Theme '{theme_id}' not found.")
    theme["theme_key"] = theme.get("slug", theme["id"])
    return theme


@router.get("/restaurants/{restaurant_id}/design")
async def get_restaurant_design(
    restaurant_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RestaurantDesignConfig).where(
        RestaurantDesignConfig.restaurant_id == restaurant.id
    )
    result = await db.execute(stmt)
    config = result.scalars().first()

    if not config:
        # Default to 'contemporary' preset
        default_preset = next(
            (p for p in THEME_PRESETS if p["theme_key"] == "contemporary"), THEME_PRESETS[0]
        )
        return {
            "restaurant_id": restaurant.id,
            "theme_key": default_preset["theme_key"],
            "tokens": default_preset["tokens"],
            "layout_config": {"type": "category_first", "card_style": "compact"},
            "custom_tokens": {},
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
        "custom_tokens": config.custom_tokens,
    }


@router.put("/restaurants/{restaurant_id}/design")
async def update_restaurant_design(
    restaurant_id: uuid.UUID,
    req: DesignConfigUpdate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
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
            is_system_preset=True,
        )
        db.add(theme)
        await db.flush()

    cfg_stmt = select(RestaurantDesignConfig).where(
        RestaurantDesignConfig.restaurant_id == restaurant.id
    )
    cfg_res = await db.execute(cfg_stmt)
    config = cfg_res.scalars().first()

    if not config:
        config = RestaurantDesignConfig(
            restaurant_id=restaurant.id,
            theme_id=theme.id,
            layout_config=req.layout_config,
            custom_tokens=req.custom_tokens,
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
    """Lists supported layout presets (ARC-08 §7, ARC-07 §4.6)."""
    from app.modules.customization.registries import layout_registry

    return layout_registry.list_all()


@router.get("/layouts/{layout_id}")
async def get_layout_definition(layout_id: str):
    """Retrieves layout definition."""
    from app.modules.customization.registries import layout_registry

    layout = layout_registry.get(layout_id)
    if not layout and not layout_id.startswith("layout-"):
        layout = layout_registry.get(f"layout-{layout_id}")
    if not layout:
        raise HTTPException(status_code=404, detail=f"Layout '{layout_id}' not found.")
    return layout


@router.get("/components")
async def list_registered_components():
    """Lists registered UI components from the component registry (ARC-08 §8, ARC-07 §4.6)."""
    from app.modules.customization.registries import component_registry

    return component_registry.list_all()


@router.get("/components/{component_id}")
async def get_component_definition(component_id: str):
    """Retrieves component definition and property schema."""
    from app.modules.customization.registries import component_registry

    comp = component_registry.get(component_id)
    if not comp:
        raise HTTPException(status_code=404, detail=f"Component '{component_id}' not found.")
    return comp
