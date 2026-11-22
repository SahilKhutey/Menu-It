"""
ModularMenu — Customization API Endpoints (ARC-08 §13, §14).
Provides draft customization lifecycle, validation, deterministic preview, and revision restoration.
"""
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.application.tenant_context import TenantContext
from app.api.dependencies.authorization import require_permission
from app.modules.identity.models import Restaurant
from app.modules.menus.models import Menu
from app.modules.customization.services import customization_service

router = APIRouter(tags=["Customization"])


# --- Pydantic Schemas for API Requests/Responses ---

class CustomizationUpdateResponse(BaseModel):
    menu_id: uuid.UUID
    revision: int
    status: str = "draft"
    configuration: Dict[str, Any]
    validation: Dict[str, Any] = Field(default_factory=lambda: {"valid": True, "errors": [], "warnings": []})


# --- Customization Draft Endpoints ---

@router.get("/menus/{menu_id}/customization")
async def get_menu_customization(
    menu_id: uuid.UUID,
    response: Response,
    tenant: TenantContext = Depends(require_permission("menu.customization.read")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves current customization draft for the menu."""
    # Verify menu belongs to tenant organization
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    record = await customization_service.get_or_create_customization(db, tenant.organization_id, menu_id)
    response.headers["ETag"] = f'"revision-{record.revision}"'
    return {
        "menu_id": menu_id,
        "revision": record.revision,
        "configuration_version": "1.0.0",
        "status": "draft",
        "configuration": record.configuration,
    }


@router.put("/menus/{menu_id}/customization", response_model=CustomizationUpdateResponse)
async def update_menu_customization(
    menu_id: uuid.UUID,
    payload: Dict[str, Any],
    response: Response,
    if_match: Optional[str] = Header(None, alias="If-Match"),
    tenant: TenantContext = Depends(require_permission("menu.customization.update")),
    db: AsyncSession = Depends(get_db),
):
    """Saves validated customization draft with optimistic concurrency check."""
    # Verify menu belongs to tenant organization
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    expected_rev: Optional[int] = None
    if if_match:
        clean_match = if_match.strip('"').replace("revision-", "")
        try:
            expected_rev = int(clean_match)
        except ValueError:
            pass

    record = await customization_service.update_customization(
        db=db,
        organization_id=tenant.organization_id,
        menu_id=menu_id,
        payload=payload,
        expected_revision=expected_rev,
        actor_id=tenant.user_id,
    )

    response.headers["ETag"] = f'"revision-{record.revision}"'
    return CustomizationUpdateResponse(
        menu_id=menu_id,
        revision=record.revision,
        configuration=record.configuration,
    )


@router.post("/menus/{menu_id}/customization/validate")
async def validate_customization_endpoint(
    menu_id: uuid.UUID,
    payload: Dict[str, Any],
    tenant: TenantContext = Depends(require_permission("menu.customization.validate")),
    db: AsyncSession = Depends(get_db),
):
    """Validates customization document without saving."""
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    result = customization_service.validate_document(payload)
    return result


@router.post("/menus/{menu_id}/customization/preview")
async def preview_customization_endpoint(
    menu_id: uuid.UUID,
    payload: Optional[Dict[str, Any]] = None,
    tenant: TenantContext = Depends(require_permission("menu.preview")),
    db: AsyncSession = Depends(get_db),
):
    """Generates preview using deterministic theme resolver."""
    # Verify menu belongs to tenant organization
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    preview_data = await customization_service.generate_preview(
        db=db,
        organization_id=tenant.organization_id,
        menu_id=menu_id,
        payload=payload,
    )
    return preview_data


@router.post("/menus/{menu_id}/customization/reset")
async def reset_customization_endpoint(
    menu_id: uuid.UUID,
    payload: Optional[Dict[str, str]] = None,
    tenant: TenantContext = Depends(require_permission("menu.customization.update")),
    db: AsyncSession = Depends(get_db),
):
    """Resets customization draft back to clean defaults."""
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    theme_id = (payload or {}).get("theme_id", "theme-minimal")
    layout_id = (payload or {}).get("layout_id", "layout-grid")

    record = await customization_service.reset_customization(
        db=db,
        organization_id=tenant.organization_id,
        menu_id=menu_id,
        theme_id=theme_id,
        layout_id=layout_id,
        actor_id=tenant.user_id,
    )
    return {
        "menu_id": menu_id,
        "revision": record.revision,
        "status": "reset",
        "configuration": record.configuration,
    }


@router.get("/menus/{menu_id}/customization/revisions")
async def list_customization_revisions(
    menu_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("menu.customization.read")),
    db: AsyncSession = Depends(get_db),
):
    """Lists historical draft revisions for the menu."""
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    revs = await customization_service.list_revisions(db, tenant.organization_id, menu_id)
    return [
        {
            "id": r.id,
            "revision": r.revision,
            "created_at": r.created_at,
            "created_by": r.created_by,
        }
        for r in revs
    ]


@router.get("/menus/{menu_id}/customization/revisions/{revision_num}")
async def get_customization_revision(
    menu_id: uuid.UUID,
    revision_num: int,
    tenant: TenantContext = Depends(require_permission("menu.customization.read")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full document of a specific revision."""
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    rev = await customization_service.get_revision(db, tenant.organization_id, menu_id, revision_num)
    return {
        "id": rev.id,
        "menu_id": rev.menu_id,
        "revision": rev.revision,
        "configuration": rev.configuration,
        "created_at": rev.created_at,
    }


@router.post("/menus/{menu_id}/customization/revisions/{revision_num}/restore")
async def restore_customization_revision(
    menu_id: uuid.UUID,
    revision_num: int,
    response: Response,
    tenant: TenantContext = Depends(require_permission("menu.customization.restore")),
    db: AsyncSession = Depends(get_db),
):
    """Restores historical revision as a new draft revision."""
    menu_res = await db.execute(
        select(Menu)
        .join(Restaurant, Menu.restaurant_id == Restaurant.id)
        .where(Menu.id == menu_id, Restaurant.organization_id == tenant.organization_id)
    )
    menu = menu_res.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found.")

    record = await customization_service.restore_revision(
        db=db,
        organization_id=tenant.organization_id,
        menu_id=menu_id,
        revision_num=revision_num,
        actor_id=tenant.user_id,
    )
    response.headers["ETag"] = f'"revision-{record.revision}"'
    return {
        "menu_id": menu_id,
        "revision": record.revision,
        "status": "restored",
        "configuration": record.configuration,
    }
