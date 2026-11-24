"""Authentication dependencies interface (FCD-04 §10.1)."""

from typing import Annotated
from uuid import UUID

from fastapi import Header, HTTPException, status

from menu_it.auth.principal import AuthenticatedPrincipal


async def get_current_principal(
    x_user_id: Annotated[
        str | None,
        Header(alias="X-User-ID", description="Authenticated user ID header"),
    ] = None,
) -> AuthenticatedPrincipal:
    """Retrieve authenticated principal.

    In production (FCD-05), this dependency decodes and verifies session tokens/JWTs.
    In FCD-04, it reads X-User-ID header for testing, raising HTTP 401 if unauthenticated.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required.",
        )
    try:
        user_uuid = UUID(x_user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identification format.",
        ) from exc

    return AuthenticatedPrincipal(user_id=user_uuid, is_authenticated=True)
