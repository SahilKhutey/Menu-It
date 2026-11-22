"""
ModularMenu — Menu Rendering API Endpoints (ARC-09 §13, WP-ARC09-13).
Provides public published rendering delivery, authorized draft previews, and render validation.
Maintains strict separation: API routes mediate database persistence while rendering engine remains pure.
"""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, verify_restaurant_access
from app.core.errors import ResourceNotFoundError
from app.modules.identity.models import Restaurant
from app.modules.menus.models import Category, Menu, MenuItem, MenuVersion, Publication
from app.modules.rendering.application.services.render_input_builder import RenderInputBuilder
from app.modules.rendering.application.services.render_input_validator import RenderInputValidator
from app.modules.rendering.domain.exceptions import RenderSnapshotNotFoundError
from app.modules.rendering.domain.render_input import RenderLayout
from app.modules.rendering.domain.render_mode import RenderMode
from app.modules.rendering.schemas.preview_render import (
    DraftPreviewMetadataOut,
    DraftPreviewResponse,
    DraftPreviewWarning,
)
from app.modules.rendering.schemas.public_render import (
    PublicCategoryOut,
    PublicItemOut,
    PublicLayoutOut,
    PublicMenuOut,
    PublicMenuRenderResponse,
    PublicMetadataOut,
    PublicRenderPlanOut,
    PublicRestaurantOut,
    PublicThemeOut,
)
from app.modules.rendering.schemas.render_input import (
    RenderValidationRequest,
    RenderValidationResponse,
)
from app.modules.themes.models import RestaurantDesignConfig, Theme
from app.modules.themes.presets import THEME_PRESETS

router = APIRouter(tags=["Menu Rendering & Delivery"])


async def resolve_public_menu(
    db: AsyncSession,
    restaurant_slug: str,
    menu_slug: str,
) -> tuple[PublicMenuRenderResponse, str, str]:
    """Resolves active published snapshot and produces PublicMenuRenderResponse."""
    # 1. Resolve active restaurant
    rest_stmt = select(Restaurant).where(
        Restaurant.slug == restaurant_slug,
        Restaurant.status == "active",
    )
    restaurant = (await db.execute(rest_stmt)).scalars().first()
    if not restaurant:
        raise RenderSnapshotNotFoundError(restaurant_slug, menu_slug)

    # 2. Resolve menu by slug
    menu_stmt = select(Menu).where(
        Menu.restaurant_id == restaurant.id,
        Menu.slug == menu_slug,
    )
    menu = (await db.execute(menu_stmt)).scalars().first()
    if not menu:
        raise RenderSnapshotNotFoundError(restaurant_slug, menu_slug)

    # 3. Resolve active publication and immutable version
    pub_stmt = (
        select(Publication, MenuVersion)
        .join(MenuVersion, MenuVersion.id == Publication.active_version_id)
        .where(
            Publication.restaurant_id == restaurant.id,
            Publication.menu_id == menu.id,
            Publication.status == "published",
        )
        .order_by(Publication.published_at.desc())
    )
    row = (await db.execute(pub_stmt)).first()
    if not row:
        raise RenderSnapshotNotFoundError(restaurant_slug, menu_slug)

    publication, menu_version = row

    render_input = RenderInputBuilder.build_from_snapshot(
        snapshot_data=menu_version.snapshot_data,
        version_number=menu_version.version_number,
        checksum=menu_version.checksum,
        published_at=menu_version.published_at.isoformat(),
        render_mode=RenderMode.PUBLIC_PUBLISHED,
    )

    plan = RenderInputBuilder.build_render_plan(render_input.layout)

    # Assemble PublicMenuRenderResponse
    response_dto = PublicMenuRenderResponse(
        status="success",
        restaurant=PublicRestaurantOut(
            id=render_input.restaurant.id,
            name=render_input.restaurant.name,
            slug=render_input.restaurant.slug,
            description=render_input.restaurant.description,
            logo_url=render_input.restaurant.logo_url,
            cover_url=render_input.restaurant.cover_url,
            currency=render_input.restaurant.currency,
            time_zone=render_input.restaurant.time_zone,
            phone=render_input.restaurant.phone,
            email=render_input.restaurant.email,
            address=render_input.restaurant.address,
        ),
        menu=PublicMenuOut(
            id=render_input.menu.id,
            name=render_input.menu.name,
            slug=render_input.menu.slug,
            description=render_input.menu.description,
            menu_type=render_input.menu.menu_type,
        ),
        categories=[
            PublicCategoryOut(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                image_url=cat.image_url,
                sort_order=cat.sort_order,
                items=[
                    PublicItemOut(
                        id=it.id,
                        name=it.name,
                        description=it.description,
                        price=float(it.price),
                        formatted_price=it.formatted_price,
                        currency_code=it.currency_code,
                        dietary_type=it.dietary_type,
                        spice_level=it.spice_level,
                        image_url=it.image_url,
                        ingredients=it.ingredients,
                        allergens=it.allergens,
                        is_available=it.is_available,
                        is_featured=it.is_featured,
                        sort_order=it.sort_order,
                        badges=it.badges,
                    )
                    for it in cat.items
                ],
            )
            for cat in render_input.categories
        ],
        theme=PublicThemeOut(
            id=render_input.theme.id,
            name=render_input.theme.name,
            mode=render_input.theme.mode,
            tokens=render_input.theme.tokens,
        ),
        layout=PublicLayoutOut(
            type=render_input.layout.type,
            card_style=render_input.layout.card_style,
            columns=render_input.layout.columns,
            density=render_input.layout.density,
            show_images=render_input.layout.show_images,
            show_descriptions=render_input.layout.show_descriptions,
            slots=render_input.layout.slots,
        ),
        render_plan=PublicRenderPlanOut(
            layout_type=plan.layout_type,
            slots=plan.slots,
            active_components=plan.active_components,
            responsive_breakpoints=plan.responsive_breakpoints,
        ),
        metadata=PublicMetadataOut(
            version_number=render_input.metadata.version_number,
            checksum=render_input.metadata.checksum,
            published_at=render_input.metadata.published_at,
            rendered_at=render_input.metadata.rendered_at,
            renderer_version=render_input.metadata.renderer_version,
        ),
    )

    etag = f'"{menu_version.checksum}"'
    cache_control = "public, max-age=60, s-maxage=300, stale-while-revalidate=86400"
    return response_dto, etag, cache_control


async def resolve_draft_preview(
    db: AsyncSession,
    restaurant: Restaurant,
    menu_id: uuid.UUID,
) -> tuple[DraftPreviewResponse, dict[str, str]]:
    """Generates an authorized draft preview for restaurant operators."""
    # 1. Fetch Menu
    menu_stmt = select(Menu).where(Menu.id == menu_id, Menu.restaurant_id == restaurant.id)
    menu = (await db.execute(menu_stmt)).scalars().first()
    if not menu:
        raise ResourceNotFoundError(f"Menu '{menu_id}' not found for restaurant '{restaurant.id}'")

    # 2. Fetch Categories
    cat_stmt = (
        select(Category)
        .where(Category.restaurant_id == restaurant.id, Category.menu_id == menu.id)
        .order_by(Category.sort_order.asc())
    )
    categories = (await db.execute(cat_stmt)).scalars().all()

    # 3. Fetch Items
    item_stmt = (
        select(MenuItem)
        .where(MenuItem.restaurant_id == restaurant.id)
        .order_by(MenuItem.sort_order.asc())
    )
    all_items = (await db.execute(item_stmt)).scalars().all()
    items_by_cat: dict[uuid.UUID, list[MenuItem]] = {}
    for it in all_items:
        items_by_cat.setdefault(it.category_id, []).append(it)

    # 4. Fetch Active Theme & Design Config
    cfg_stmt = select(RestaurantDesignConfig).where(
        RestaurantDesignConfig.restaurant_id == restaurant.id
    )
    design_config = (await db.execute(cfg_stmt)).scalars().first()

    tokens = THEME_PRESETS[0]["tokens"]
    layout_dict = {"type": "category_first", "card_style": "compact"}
    theme_id = "preset-classic-slate"
    theme_name = "Classic Slate"

    if design_config:
        layout_dict = design_config.layout_config or layout_dict
        theme_stmt = select(Theme).where(Theme.id == design_config.theme_id)
        theme_record = (await db.execute(theme_stmt)).scalars().first()
        if theme_record:
            tokens = {**theme_record.tokens, **(design_config.custom_tokens or {})}
            theme_id = str(theme_record.id)
            theme_name = theme_record.name

    # 5. Assemble Categories and Items
    categories_out: list[PublicCategoryOut] = []
    warnings: list[DraftPreviewWarning] = []

    currency_code = getattr(restaurant, "currency", "INR")

    for cat in categories:
        items_out: list[PublicItemOut] = []
        for it in items_by_cat.get(cat.id, []):
            price_val = float(it.base_price)
            formatted_price = RenderInputBuilder.format_price(
                Decimal(str(price_val)), it.currency_code or currency_code
            )

            badges = []
            if it.dietary_type:
                badges.append(it.dietary_type.capitalize())
            if it.is_featured:
                badges.append("Featured")

            spice_raw = it.spice_level
            spice_level_int = 0
            if isinstance(spice_raw, int):
                spice_level_int = spice_raw
            elif isinstance(spice_raw, str):
                spice_map = {"none": 0, "mild": 1, "medium": 2, "hot": 3, "extra_hot": 4}
                spice_level_int = spice_map.get(spice_raw.lower(), 1 if spice_raw else 0)

            if spice_level_int > 0:
                badges.append(f"Spicy {spice_level_int}/3")

            if not it.description:
                warnings.append(
                    DraftPreviewWarning(
                        code="MISSING_DESCRIPTION",
                        message=f"Item '{it.name}' lacks a description",
                        field=f"item:{it.id}:description",
                    )
                )
            if not it.image_url:
                warnings.append(
                    DraftPreviewWarning(
                        code="MISSING_IMAGE",
                        message=f"Item '{it.name}' has no photo attached",
                        field=f"item:{it.id}:image_url",
                    )
                )

            items_out.append(
                PublicItemOut(
                    id=str(it.id),
                    name=it.name,
                    description=it.description,
                    price=price_val,
                    formatted_price=formatted_price,
                    currency_code=it.currency_code or currency_code,
                    dietary_type=it.dietary_type,
                    spice_level=spice_level_int,
                    image_url=it.image_url,
                    ingredients=it.ingredients or [],
                    allergens=it.allergens or [],
                    is_available=it.is_available,
                    is_featured=it.is_featured,
                    sort_order=it.sort_order,
                    badges=badges,
                )
            )

        categories_out.append(
            PublicCategoryOut(
                id=str(cat.id),
                name=cat.name,
                description=cat.description,
                image_url=cat.image_url,
                sort_order=cat.sort_order,
                items=items_out,
            )
        )

    # Build plan
    default_slots = {
        "header": "RestaurantHeroHeader",
        "navigation": "CategoryPillNav",
        "category_section": "CategorySection",
        "item_card": "FoodItemCard",
        "footer": "MenuFooter",
    }
    slots = {**default_slots, **layout_dict.get("slots", {})}
    render_layout = RenderLayout(
        type=layout_dict.get("type", "category_first"),
        card_style=layout_dict.get("card_style", "compact"),
        columns=int(layout_dict.get("columns", 1)),
        density=layout_dict.get("density", "comfortable"),
        show_images=layout_dict.get("show_images", True),
        show_descriptions=layout_dict.get("show_descriptions", True),
        slots=slots,
    )
    plan = RenderInputBuilder.build_render_plan(render_layout)

    now_str = datetime.now(UTC).isoformat()
    response_dto = DraftPreviewResponse(
        status="preview",
        restaurant=PublicRestaurantOut(
            id=str(restaurant.id),
            name=restaurant.name,
            slug=restaurant.slug,
            description=restaurant.description,
            logo_url=restaurant.logo_url,
            cover_url=restaurant.cover_url,
            currency=currency_code,
            time_zone=getattr(restaurant, "time_zone", "Asia/Kolkata"),
            phone=getattr(restaurant, "phone", None),
            email=getattr(restaurant, "email", None),
            address=getattr(restaurant, "address", None),
        ),
        menu=PublicMenuOut(
            id=str(menu.id),
            name=menu.name,
            slug=menu.slug,
            description=menu.description,
            menu_type=menu.menu_type,
        ),
        categories=categories_out,
        theme=PublicThemeOut(
            id=theme_id,
            name=theme_name,
            mode="light",
            tokens=tokens,
        ),
        layout=PublicLayoutOut(
            type=render_layout.type,
            card_style=render_layout.card_style,
            columns=render_layout.columns,
            density=render_layout.density,
            show_images=render_layout.show_images,
            show_descriptions=render_layout.show_descriptions,
            slots=render_layout.slots,
        ),
        render_plan=PublicRenderPlanOut(
            layout_type=plan.layout_type,
            slots=plan.slots,
            active_components=plan.active_components,
            responsive_breakpoints=plan.responsive_breakpoints,
        ),
        metadata=DraftPreviewMetadataOut(
            is_preview=True,
            draft_version_id=str(menu.id),
            generated_at=now_str,
            renderer_version="1.0.0",
            watermark_text="PREVIEW - UNPUBLISHED DRAFT",
            warnings=warnings,
        ),
    )

    headers = {
        "Cache-Control": "private, no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return response_dto, headers


# --- Endpoints ---


@router.get(
    "/public/restaurants/{restaurant_slug}/menus/{menu_slug}/render",
    response_model=PublicMenuRenderResponse,
    summary="Get Canonical Public Rendered Menu",
)
async def get_public_rendered_menu(
    restaurant_slug: str,
    menu_slug: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the canonical rendered menu for public consumers (ARC-09 §5).
    Supports HTTP caching, ETag validation, and 304 Not Modified.
    """
    try:
        dto, etag, cache_control = await resolve_public_menu(db, restaurant_slug, menu_slug)
    except RenderSnapshotNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No published menu found for restaurant '{restaurant_slug}' and menu '{menu_slug}'",
        )

    # Check Conditional If-None-Match
    if_none_match = request.headers.get("if-none-match")
    if if_none_match and (
        if_none_match == etag or if_none_match == f"W/{etag}" or if_none_match == "*"
    ):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = cache_control
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED,
            headers={"ETag": etag, "Cache-Control": cache_control},
        )

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = cache_control
    response.headers["Vary"] = "Accept-Encoding"
    return dto


@router.post(
    "/restaurants/{restaurant_id}/menus/{menu_id}/preview",
    response_model=DraftPreviewResponse,
    summary="Get Draft Menu Preview",
)
async def get_draft_preview(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    response: Response,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates an authorized draft preview for restaurant operators (ARC-09 §3).
    Includes unpublished changes, watermarking, and prevents upstream HTTP caching.
    """
    try:
        dto, headers = await resolve_draft_preview(db, restaurant, menu_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    for k, v in headers.items():
        response.headers[k] = v
    return dto


@router.post(
    "/restaurants/{restaurant_id}/menus/{menu_id}/render-validation",
    response_model=RenderValidationResponse,
    summary="Validate Menu Rendering Readiness",
)
async def validate_menu_rendering(
    restaurant_id: uuid.UUID,
    menu_id: uuid.UUID,
    payload: RenderValidationRequest | None = None,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db),
):
    """
    Validates that a menu is structurally and visually ready to render (ARC-09 §11).
    Checks price positivity, currency format, component registrations, and required tokens.
    """
    try:
        preview_dto, _ = await resolve_draft_preview(db, restaurant, menu_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    # Convert DTO to dict for validation checks
    raw_data = preview_dto.model_dump()
    return RenderInputValidator.validate_payload(raw_data)
