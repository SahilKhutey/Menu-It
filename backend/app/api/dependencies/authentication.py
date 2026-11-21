"""
ModularMenu — API Authentication Dependencies (ARC-07 §6.1, §6.2).
Supports first-party cookie sessions and external Bearer tokens without information leakage.
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from fastapi import Cookie, Depends, Header, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.identity.models import User

security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedActor:
    user_id: UUID
    email: str
    is_platform_admin: bool
    status: str


async def get_current_actor(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    session_id: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedActor:
    """
    Resolves the authenticated actor from either Authorization Bearer token
    or server-side session cookie (ARC-07 §6.1).
    """
    token_str: Optional[str] = None
    if credentials:
        token_str = credentials.credentials
    elif session_id:
        token_str = session_id

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = decode_access_token(token_str)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed credentials identifier",
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account inactive, revoked, or not found",
        )

    return AuthenticatedActor(
        user_id=user.id,
        email=user.email,
        is_platform_admin=bool(getattr(user, "is_platform_admin", False)),
        status=user.status,
    )


async def get_current_user_legacy(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Backward-compatible dependency returning the SQLAlchemy User model."""
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
        user_uuid = UUID(user_id_str)
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
    return user
