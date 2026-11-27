"""Integration tests for durable idempotency support (FCD-07 WP-11)."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.authentication.tokens import create_access_token
from menu_it.core.config import get_settings
from menu_it.database.models.organization import Organization, OrganizationStatus
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_idempotency_workflow(
    authed_client,
    db_session: AsyncSession,
) -> None:
    settings = get_settings()

    # 1. Setup Tenant Organization
    org = Organization(
        name="Idempotency Org",
        slug=f"idem-org-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.flush()

    # 2. Setup User & Membership
    user = User(
        email=f"idem-{uuid4().hex[:6]}@example.com",
        normalized_email=f"idem-{uuid4().hex[:6]}@example.com",
        display_name="Idem User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(membership)
    await db_session.flush()

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

    idem_key = f"key-{uuid4().hex}"
    base_headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org.id),
        "Idempotency-Key": idem_key,
    }

    payload1 = {
        "name": "Original Restaurant",
        "slug": f"orig-{uuid4().hex[:6]}",
        "timezone": "UTC",
    }

    # First request -> 201 Created
    res1 = authed_client.post(
        "/api/v1/restaurants",
        headers=base_headers,
        json=payload1,
    )
    assert res1.status_code == 201
    body1 = res1.json()
    assert body1["success"] is True
    assert body1["data"]["name"] == "Original Restaurant"
    created_id = body1["data"]["id"]

    # Replay request with exact same key and payload -> 201 with Idempotent-Replay header
    res2 = authed_client.post(
        "/api/v1/restaurants",
        headers=base_headers,
        json=payload1,
    )
    assert res2.status_code == 201
    assert res2.headers.get("Idempotent-Replay") == "true"
    assert res2.headers.get("X-Cache-Lookup") == "HIT"
    body2 = res2.json()
    assert body2["data"]["id"] == created_id

    # Conflict request with same key but differing payload -> 409 IDEMPOTENCY_CONFLICT
    payload_diff = {
        "name": "Different Restaurant Name",
        "slug": f"diff-{uuid4().hex[:6]}",
        "timezone": "Europe/London",
    }
    res3 = authed_client.post(
        "/api/v1/restaurants",
        headers=base_headers,
        json=payload_diff,
    )
    assert res3.status_code == 409
    body3 = res3.json()
    assert body3["success"] is False
    assert body3["error"]["code"] == "IDEMPOTENCY_CONFLICT"
    assert "idempotency conflict" in body3["error"]["message"].lower()
