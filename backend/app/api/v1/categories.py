"""
ModularMenu — Category Management API Endpoints (ARC-07 §4.4).
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.api.dependencies.tenant import get_tenant_context
from app.api.schemas.categories import CategoryResponse, CategoryUpdateRequest
from app.api.schemas.items import ItemCreateRequest, ItemResponse
from app.core.database import get_db
from app.modules.menus.models import Category, MenuItem
from app.shared.application.tenant_context import TenantContext

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdateRequest,
    tenant: TenantContext = Depends(require_permission("category.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Updates category properties within the authorized tenant."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, val)

    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("category.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Deletes or archives a category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalars().first()
    if category:
        await db.delete(category)
        await db.commit()
    return None


@router.get("/{category_id}/items", response_model=List[ItemResponse])
async def list_category_items(
    category_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("menu.read")),
    db: AsyncSession = Depends(get_db),
):
    """Lists food items under a specific category."""
    stmt = (
        select(MenuItem)
        .where(MenuItem.category_id == category_id)
        .order_by(MenuItem.sort_order.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{category_id}/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_category_item(
    category_id: uuid.UUID,
    payload: ItemCreateRequest,
    tenant: TenantContext = Depends(require_permission("item.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new food item under the specified category."""
    # Verify category exists
    cat_res = await db.execute(select(Category).where(Category.id == category_id))
    category = cat_res.scalars().first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    item = MenuItem(
        restaurant_id=category.restaurant_id,
        category_id=category.id,
        name=payload.name,
        description=payload.description,
        base_price=payload.default_price or 0,
        currency_code=payload.currency,
        dietary_type=payload.dietary_classification,
        allergens=payload.allergens,
        is_available=payload.is_available,
        sort_order=payload.sort_order,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
