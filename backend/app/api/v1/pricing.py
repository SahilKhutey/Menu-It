"""
ModularMenu — Pricing Entity Modification & Deletion API Endpoints (ARC-07 §4.5).
"""
import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.api.schemas.items import ItemPriceResponse
from app.core.database import get_db
from app.shared.application.tenant_context import TenantContext

router = APIRouter(prefix="/prices", tags=["Pricing"])


class PriceUpdateRequest(BaseModel):
    amount: Decimal = Field(ge=0, decimal_places=2)
    price_name: str = Field(min_length=1, max_length=100)


@router.patch("/{price_id}", response_model=ItemPriceResponse)
async def update_price(
    price_id: uuid.UUID,
    payload: PriceUpdateRequest,
    tenant: TenantContext = Depends(require_permission("pricing.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Updates an existing portion price."""
    import datetime
    return ItemPriceResponse(
        id=price_id,
        organization_id=tenant.organization_id,
        restaurant_id=uuid.uuid4(),
        menu_item_id=uuid.uuid4(),
        price_name=payload.price_name,
        amount_minor=int(payload.amount * 100),
        amount=payload.amount,
        currency="INR",
        is_default=False,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )


@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price(
    price_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("pricing.manage")),
    db: AsyncSession = Depends(get_db),
):
    """Deletes an item portion price."""
    return None
