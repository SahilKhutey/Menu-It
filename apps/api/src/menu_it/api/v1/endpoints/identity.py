"""Identity endpoints for current user profile inspection and updates (FCD-05 §18)."""

import contextlib
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.database.models.user import User
from menu_it.database.session import get_db_session
from menu_it.identity.schemas import (
    UserProfileUpdateRequest,
    UserResponse,
)
from menu_it.schemas.common import APIResponse, ResponseMetadata

router = APIRouter(
    prefix="/identity",
    tags=["Identity"],
)


def _meta(req_id_str: str | None) -> ResponseMetadata:
    req_uuid = UUID(int=0)
    if req_id_str:
        with contextlib.suppress(ValueError):
            req_uuid = UUID(req_id_str)
    return ResponseMetadata(request_id=req_uuid)


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get Current User Profile",
)
async def get_current_user_profile(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[UserResponse]:
    """Retrieve safe identity profile for the currently authenticated user."""
    user = await session.get(User, principal.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found.",
        )

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
        meta=_meta(x_request_id),
    )


@router.patch(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Update Current User Profile",
)
async def update_current_user_profile(
    payload: UserProfileUpdateRequest,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[UserResponse]:
    """Update non-sensitive profile attributes for the authenticated user."""
    user = await session.get(User, principal.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found.",
        )

    if payload.display_name is not None:
        user.display_name = payload.display_name.strip()

    await session.commit()
    await session.refresh(user)

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
        meta=_meta(x_request_id),
    )
