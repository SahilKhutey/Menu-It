"""Authentication dependencies interface (FCD-05 §12.2)."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.authentication.tokens import (
    TokenError,
    TokenExpiredError,
    decode_access_token,
)
from menu_it.core.config import get_settings
from menu_it.database.models.user import User, UserStatus
from menu_it.database.session import get_db_session
from menu_it.sessions.service import SessionService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_principal(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ] = None,
    session: Annotated[
        AsyncSession | None,
        Depends(get_db_session),
    ] = None,
    x_user_id: Annotated[
        str | None,
        Header(alias="X-User-ID", description="Development/testing user ID fallback header"),
    ] = None,
) -> AuthenticatedPrincipal:
    """Retrieve authenticated principal validating JWT, session state, and user active status."""
    settings = get_settings()

    # 1. Bearer Token Authentication (Primary FCD-05 flow)
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        try:
            payload = decode_access_token(
                token=token,
                verification_key=settings.auth_secret_key,
                allowed_algorithms=[settings.auth_jwt_algorithm, "RS256", "EdDSA"],
                issuer=settings.auth_issuer,
                audience=settings.auth_audience,
            )
            user_id = UUID(str(payload["sub"]))
            session_id = UUID(str(payload["sid"]))
        except TokenExpiredError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token has expired.",
                headers={
                    "WWW-Authenticate": (
                        'Bearer error="invalid_token", error_description="token expired"'
                    )
                },
            ) from exc
        except TokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {exc}",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            ) from exc
        except (KeyError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        # Validate active session and user in database
        if session:
            session_svc = SessionService(session)
            user_session = await session_svc.validate_session(session_id)
            if not user_session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session is no longer valid or has been revoked.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user = await session.get(User, user_id)
            if not user or user.status not in (UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive or suspended.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return AuthenticatedPrincipal(
            user_id=user_id,
            session_id=session_id,
            is_authenticated=True,
        )

    # 2. Testing / Fallback Header (FCD-04 compatibility)
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identification format.",
            ) from exc
        return AuthenticatedPrincipal(user_id=user_uuid, is_authenticated=True)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication credentials are required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
