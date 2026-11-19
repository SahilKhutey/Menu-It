import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, get_db, verify_restaurant_access
from app.modules.identity.models import Organization, Restaurant, RestaurantMember, User
from app.modules.identity.schemas import RestaurantCreate, RestaurantOut, RestaurantUpdate

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("", response_model=List[RestaurantOut])
async def list_restaurants(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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


@router.get("/{restaurant_id}", response_model=RestaurantOut)
async def get_restaurant(
    restaurant_id: uuid.UUID,
    restaurant: Restaurant = Depends(verify_restaurant_access)
):
    return restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantOut)
async def update_restaurant(
    restaurant_id: uuid.UUID,
    req: RestaurantUpdate,
    restaurant: Restaurant = Depends(verify_restaurant_access),
    db: AsyncSession = Depends(get_db)
):
    for field, val in req.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, val)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant
