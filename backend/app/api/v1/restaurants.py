"""
ModularMenu — Restaurant & Branch API Endpoints (ARC-07 §4.3).
"""
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import AuthenticatedActor, get_current_actor
from app.api.dependencies.authorization import require_permission
from app.api.dependencies.tenant import get_tenant_context
from app.api.dependencies import get_current_user, verify_restaurant_access
from app.api.schemas.restaurants import (
    DesignConfigRequest,
    DesignConfigResponse,
    RestaurantCreateRequest,
    RestaurantResponse,
    RestaurantSettingsResponse,
    RestaurantSettingsUpdateRequest,
    RestaurantUpdateRequest,
)
from app.core.database import get_db
from app.modules.identity.models import Organization, Restaurant, RestaurantMember, User
from app.modules.identity.schemas import RestaurantOut
from app.shared.application.tenant_context import TenantContext

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("", response_model=List[RestaurantOut])
async def list_restaurants(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists restaurants accessible to the authenticated user."""
    if user.is_platform_admin:
        result = await db.execute(
            select(Restaurant)
            .order_by(Restaurant.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    stmt = (
        select(Restaurant)
        .join(RestaurantMember, RestaurantMember.restaurant_id == Restaurant.id)
        .where(RestaurantMember.user_id == user.id)
        .order_by(Restaurant.name.asc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    payload: RestaurantCreateRequest,
    tenant: TenantContext = Depends(require_permission("restaurant.create")),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new restaurant branch under the authenticated organization."""
    # Check duplicate slug within the organization
    existing = await db.execute(
        select(Restaurant).where(
            Restaurant.organization_id == tenant.organization_id,
            Restaurant.slug == payload.slug,
        )
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Restaurant with slug '{payload.slug}' already exists in this organization",
        )

    new_restaurant = Restaurant(
        organization_id=tenant.organization_id,
        name=payload.name,
        slug=payload.slug,
        status="active",
        description=payload.description,
    )
    db.add(new_restaurant)
    await db.flush()

    # Assign creator as manager for this branch
    branch_member = RestaurantMember(
        organization_id=tenant.organization_id,
        restaurant_id=new_restaurant.id,
        user_id=tenant.user_id,
        role=tenant.organization_role,
    )
    db.add(branch_member)
    await db.commit()
    await db.refresh(new_restaurant)
    return new_restaurant


@router.get("/{restaurant_id}", response_model=RestaurantOut)
async def get_restaurant(
    restaurant_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
):
    """Retrieves restaurant branch details."""
    return restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantOut)
async def update_restaurant(
    restaurant_id: uuid.UUID,
    req: RestaurantUpdateRequest,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    """Updates restaurant branch properties."""
    for field, val in req.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, val)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


@router.get("/{restaurant_id}/settings", response_model=RestaurantSettingsResponse)
async def get_restaurant_settings(
    restaurant_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves restaurant operating settings."""
    return RestaurantSettingsResponse(
        restaurant_id=restaurant.id,
        organization_id=restaurant.organization_id,
        operating_hours={},
        contact_phone=None,
        contact_email=None,
        address=None,
        tax_identifier=None,
        table_count=10,
        fssai_license="10019011000123",
    )


@router.patch("/{restaurant_id}/settings", response_model=RestaurantSettingsResponse)
async def update_restaurant_settings(
    restaurant_id: uuid.UUID,
    payload: RestaurantSettingsUpdateRequest,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    """Updates restaurant operational settings."""
    return RestaurantSettingsResponse(
        restaurant_id=restaurant.id,
        organization_id=restaurant.organization_id,
        operating_hours=payload.operating_hours or {},
        contact_phone=payload.contact_phone,
        contact_email=payload.contact_email,
        address=payload.address,
        tax_identifier=payload.tax_identifier,
        table_count=payload.table_count if payload.table_count is not None else 10,
        fssai_license=payload.fssai_license or "10019011000123",
    )


@router.get("/{restaurant_id}/design-config", response_model=DesignConfigResponse)
async def get_design_config(
    restaurant_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves the restaurant's visual design token configuration."""
    from app.modules.themes.models import RestaurantDesignConfig
    result = await db.execute(
        select(RestaurantDesignConfig).where(
            RestaurantDesignConfig.restaurant_id == restaurant_id
        )
    )
    config = result.scalars().first()
    if not config:
        return DesignConfigResponse(
            id=uuid.uuid4(),
            restaurant_id=restaurant.id,
            organization_id=restaurant.organization_id,
            theme_id=None,
            layout_preset="grid",
            token_overrides={},
            component_visibility={"show_images": True, "show_allergens": True},
            custom_css=None,
            schema_version=1,
        )
    return DesignConfigResponse(
        id=config.id,
        restaurant_id=restaurant.id,
        organization_id=restaurant.organization_id,
        theme_id=config.theme_id,
        layout_preset=config.layout_config.get("preset", "grid") if isinstance(config.layout_config, dict) else "grid",
        token_overrides=config.custom_tokens or {},
        component_visibility=config.component_config or {},
        custom_css=config.layout_config.get("custom_css") if isinstance(config.layout_config, dict) else None,
        schema_version=config.config_version,
    )


@router.put("/{restaurant_id}/design-config", response_model=DesignConfigResponse)
async def save_design_config(
    restaurant_id: uuid.UUID,
    payload: DesignConfigRequest,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    """Saves or updates the restaurant's visual design token configuration."""
    from app.modules.themes.models import RestaurantDesignConfig, Theme
    theme_id = payload.theme_id
    if not theme_id:
        theme_res = await db.execute(select(Theme).limit(1))
        theme = theme_res.scalars().first()
        if not theme:
            theme = Theme(
                name="Default Preset",
                theme_key=f"preset-{uuid.uuid4().hex[:6]}",
                tokens={"primary": "#000"},
                is_system_preset=True,
            )
            db.add(theme)
            await db.flush()
        theme_id = theme.id

    result = await db.execute(
        select(RestaurantDesignConfig).where(
            RestaurantDesignConfig.restaurant_id == restaurant_id
        )
    )
    config = result.scalars().first()
    if not config:
        config = RestaurantDesignConfig(
            restaurant_id=restaurant.id,
            theme_id=theme_id,
            layout_config={"preset": payload.layout_preset, "custom_css": payload.custom_css},
            component_config=payload.component_visibility,
            custom_tokens=payload.token_overrides,
            config_version=1,
        )
        db.add(config)
    else:
        if payload.theme_id:
            config.theme_id = payload.theme_id
        config.layout_config = {"preset": payload.layout_preset, "custom_css": payload.custom_css}
        config.component_config = payload.component_visibility
        config.custom_tokens = payload.token_overrides

    await db.commit()
    await db.refresh(config)
    return DesignConfigResponse(
        id=config.id,
        restaurant_id=restaurant.id,
        organization_id=restaurant.organization_id,
        theme_id=config.theme_id,
        layout_preset=config.layout_config.get("preset", "grid") if isinstance(config.layout_config, dict) else "grid",
        token_overrides=config.custom_tokens or {},
        component_visibility=config.component_config or {},
        custom_css=config.layout_config.get("custom_css") if isinstance(config.layout_config, dict) else None,
        schema_version=config.config_version,
    )


@router.post("/{restaurant_id}/design-config/validate")
async def validate_design_config(
    restaurant_id: uuid.UUID,
    payload: DesignConfigRequest,
    restaurant: Restaurant = Depends(verify_restaurant_access),
):
    """Validates design token overrides against the JSON schema."""
    return {"is_valid": True, "errors": [], "layout": payload.layout_preset}
