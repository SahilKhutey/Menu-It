"""Session management endpoints for active device listings and revocations (FCD-05 §18)."""

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
from menu_it.authentication.schemas import SessionResponse
from menu_it.database.session import get_db_session
from menu_it.schemas.common import APIResponse, ResponseMetadata
from menu_it.sessions.exceptions import SessionNotFoundError
from menu_it.sessions.service import SessionService

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


def _meta(req_id_str: str | None) -> ResponseMetadata:
    req_uuid = UUID(int=0)
    if req_id_str:
        with contextlib.suppress(ValueError):
            req_uuid = UUID(req_id_str)
    return ResponseMetadata(request_id=req_uuid)


@router.get(
    "",
    response_model=APIResponse[list[SessionResponse]],
    summary="List Active User Sessions",
)
async def list_active_sessions(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[list[SessionResponse]]:
    """List all active device sessions for the authenticated user."""
    session_svc = SessionService(session)
    active_sessions = await session_svc.list_user_sessions(principal.user_id)

    return APIResponse(
        success=True,
        data=[SessionResponse.model_validate(s) for s in active_sessions],
        meta=_meta(x_request_id),
    )


@router.delete(
    "/{session_id}",
    response_model=APIResponse[dict[str, str]],
    summary="Revoke Specific User Session",
)
async def revoke_user_session(
    session_id: UUID,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Revoke a specific device session owned by the authenticated user."""
    session_svc = SessionService(session)
    try:
        await session_svc.revoke_session(principal.user_id, session_id)
        await session.commit()
    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not owned by caller.",
        ) from exc

    return APIResponse(
        success=True,
        data={"message": f"Session '{session_id}' has been revoked."},
        meta=_meta(x_request_id),
    )
