"""
ModularMenu — API Dependencies Package (ARC-07 §14.1).
Exports authentication, authorization, tenant context, pagination, and database session providers.
"""
import uuid
from typing import Callable, List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import AuthenticatedActor, get_current_actor
from app.api.dependencies.authorization import require_permission
from app.api.dependencies.pagination import CursorPaginationMeta, PaginatedResponse, PaginationParams
from app.api.dependencies.tenant import get_tenant_context
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.tenant_context import set_current_restaurant_id, set_current_user_id
from app.modules.identity.models import Restaurant, RestaurantMember, User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_id_str = decode_access_token(token)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user identifier",
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account inactive or not found",
        )

    set_current_user_id(user.id)
    return user


async def verify_restaurant_access(
    restaurant_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Restaurant:
    if user.is_platform_admin:
        result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        restaurant = result.scalars().first()
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
        set_current_restaurant_id(restaurant.id)
        return restaurant

    stmt = select(RestaurantMember).where(
        RestaurantMember.restaurant_id == restaurant_id,
        RestaurantMember.user_id == user.id,
    )
    result = await db.execute(stmt)
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission for this restaurant tenant.",
        )

    res_stmt = select(Restaurant).where(Restaurant.id == restaurant_id)
    res_result = await db.execute(res_stmt)
    restaurant = res_result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    set_current_restaurant_id(restaurant.id)
    return restaurant


def require_role(allowed_roles: List[str]) -> Callable:
    async def role_checker(
        restaurant_id: uuid.UUID,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        if user.is_platform_admin:
            return

        stmt = select(RestaurantMember).where(
            RestaurantMember.restaurant_id == restaurant_id,
            RestaurantMember.user_id == user.id,
        )
        result = await db.execute(stmt)
        membership = result.scalars().first()

        if not membership or membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of the following roles: {allowed_roles}",
            )

    return role_checker


async def require_platform_admin(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform administration privileges required.",
        )
    return user


__all__ = [
    "AuthenticatedActor",
    "get_current_actor",
    "get_current_user",
    "verify_restaurant_access",
    "require_role",
    "require_platform_admin",
    "require_permission",
    "get_tenant_context",
    "PaginationParams",
    "PaginatedResponse",
    "CursorPaginationMeta",
    "get_db",
]
