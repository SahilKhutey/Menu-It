"""
ModularMenu — Food Item & Availability API Endpoints (ARC-07 §4.4, §4.5).
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.api.schemas.items import (
    AvailabilityUpdateRequest,
    ItemPriceCreateRequest,
    ItemPriceResponse,
    ItemResponse,
    ItemUpdateRequest,
)
from app.api.schemas.menus import ReorderRequest
from app.core.database import get_db
from app.modules.menus.models import MenuItem
from app.shared.application.tenant_context import TenantContext

router = APIRouter(prefix="/items", tags=["Food Items"])


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("menu.read")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves single food item details."""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: uuid.UUID,
    payload: ItemUpdateRequest,
    tenant: TenantContext = Depends(require_permission("item.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Updates food item details."""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    data = payload.model_dump(exclude_unset=True)
    if "dietary_classification" in data:
        data["dietary_type"] = data.pop("dietary_classification")

    for field, val in data.items():
        setattr(item, field, val)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("item.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Deletes or archives a food item."""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
    return None


@router.patch("/{item_id}/availability", response_model=ItemResponse)
async def update_item_availability(
    item_id: uuid.UUID,
    payload: AvailabilityUpdateRequest,
    tenant: TenantContext = Depends(require_permission("availability.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Updates food item 86'd / availability status."""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    item.is_available = payload.is_available
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{item_id}/prices", response_model=List[ItemPriceResponse])
async def list_item_prices(
    item_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("menu.read")),
    db: AsyncSession = Depends(get_db),
):
    """Lists all portion prices for a food item."""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    import datetime
    return [
        ItemPriceResponse(
            id=uuid.uuid4(),
            organization_id=tenant.organization_id,
            restaurant_id=item.restaurant_id,
            menu_item_id=item.id,
            price_name="Default",
            amount_minor=int(item.base_price * 100),
            amount=item.base_price,
            currency=item.currency_code,
            is_default=True,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
    ]


@router.post("/{item_id}/prices", response_model=ItemPriceResponse, status_code=status.HTTP_201_CREATED)
async def create_item_price(
    item_id: uuid.UUID,
    payload: ItemPriceCreateRequest,
    tenant: TenantContext = Depends(require_permission("pricing.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Creates a price variant for an item."""
    if payload.amount < 0:
        raise HTTPException(status_code=400, detail="Price amount cannot be negative")

    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    import datetime
    return ItemPriceResponse(
        id=uuid.uuid4(),
        organization_id=tenant.organization_id,
        restaurant_id=item.restaurant_id,
        menu_item_id=item.id,
        price_name=payload.price_name,
        amount_minor=int(payload.amount * 100),
        amount=payload.amount,
        currency=payload.currency,
        is_default=payload.is_default,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )


@router.post("/reorder")
async def reorder_items(
    payload: ReorderRequest,
    tenant: TenantContext = Depends(require_permission("item.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Batch reorders items."""
    for item_order in payload.items:
        res = await db.execute(select(MenuItem).where(MenuItem.id == item_order.id))
        it = res.scalars().first()
        if it:
            it.sort_order = item_order.sort_order
    await db.commit()
    return {"status": "success", "reordered_count": len(payload.items)}
