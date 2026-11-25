"""Integration tests for platform notification API endpoints (FCD-09 WP-03)."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import create_access_token
from menu_it.core.config import get_settings
from menu_it.database.models.notification import NotificationModel
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_notification_api_list_and_mark_read(
    authed_client,
    db_session: AsyncSession,
) -> None:
    settings = get_settings()

    user = User(
        email=f"recipient-{uuid4().hex[:6]}@domain.com",
        normalized_email=f"recipient-{uuid4().hex[:6]}@domain.com",
        display_name="Recipient User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Pre-populate two notifications: one unread, one read
    notif1 = NotificationModel(
        id=uuid4(),
        organization_id=None,
        recipient_user_id=user.id,
        type="account-welcome",
        title="Welcome to Menu-It!",
        body="Your account is active.",
        read_at=None,
    )
    notif2 = NotificationModel(
        id=uuid4(),
        organization_id=None,
        recipient_user_id=user.id,
        type="order-status",
        title="Order #101 Updated",
        body="Order ready.",
        read_at=None,
    )
    db_session.add_all([notif1, notif2])

    session_service = SessionService(db_session)
    sess, _ = await session_service.create_session(user_id=user.id)
    await db_session.commit()

    token = create_access_token(
        user_id=user.id,
        session_id=sess.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List notifications
    list_res = authed_client.get("/api/v1/notifications", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()["data"]
    assert len(items) == 2

    # 2. Mark notif1 as read
    read_res = authed_client.patch(f"/api/v1/notifications/{notif1.id}/read", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["data"]["status"] == "read"

    # 3. List with unread_only=true
    unread_res = authed_client.get("/api/v1/notifications?unread_only=true", headers=headers)
    assert unread_res.status_code == 200
    unread_items = unread_res.json()["data"]
    assert len(unread_items) == 1
    assert unread_items[0]["id"] == str(notif2.id)
