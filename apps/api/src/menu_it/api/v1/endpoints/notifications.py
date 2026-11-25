"""In-app notifications API endpoints (FCD-09 WP-03)."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict

from menu_it.api.dependencies.authentication import get_authenticated_principal
from menu_it.api.dependencies.tenant import get_optional_organization_id
from menu_it.api.schemas.common import APIResponse, ResponseMeta
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.platform.notifications.application.service import NotificationService
from menu_it.platform.notifications.dependencies import get_notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


class NotificationItem(BaseModel):
    """In-app notification item representation."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    type: str
    title: str
    body: str
    read_at: datetime | None
    created_at: datetime


@router.get(
    "",
    response_model=APIResponse[list[NotificationItem]],
    summary="List In-App Notifications",
)
async def list_notifications(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    unread_only: bool = Query(default=False, description="Filter for unread notifications only"),
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[list[NotificationItem]]:
    """List in-app notifications for the authenticated user, scoped to active tenant context."""
    records = await service.list_in_app(
        recipient_user_id=principal.user_id,
        organization_id=organization_id,
        unread_only=unread_only,
    )

    items = [
        NotificationItem(
            id=r.id,
            type=r.type,
            title=r.title,
            body=r.body,
            read_at=r.read_at,
            created_at=r.created_at,
        )
        for r in records
    ]

    return APIResponse(
        success=True,
        data=items,
        meta=ResponseMeta(request_id=x_request_id or "notifications-list"),
    )


@router.patch(
    "/{notification_id}/read",
    response_model=APIResponse[dict[str, str]],
    summary="Mark Notification as Read",
)
async def mark_notification_read(
    notification_id: UUID,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Mark an in-app notification as read for the authenticated recipient."""
    success = await service.mark_in_app_read(
        notification_id=notification_id,
        recipient_user_id=principal.user_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification '{notification_id}' not found or already read.",
        )

    return APIResponse(
        success=True,
        data={"id": str(notification_id), "status": "read"},
        meta=ResponseMeta(request_id=x_request_id or str(notification_id)),
    )
