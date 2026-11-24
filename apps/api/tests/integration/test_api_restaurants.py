"""Integration tests for restaurant API endpoints and tenant scoping (FCD-07 WP-09)."""

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
from menu_it.database.models.restaurant import Restaurant, RestaurantStatus
from menu_it.database.models.user import User, UserStatus
from menu_it.sessions.service import SessionService


@pytest.mark.asyncio
async def test_restaurant_endpoints_lifecycle(
    authed_client,
    db_session: AsyncSession,
) -> None:
    settings = get_settings()

    # 1. Setup Tenant Organization
    org = Organization(
        name="Dining Hall",
        slug=f"dining-hall-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org)
    await db_session.flush()

    # 2. Setup User & Membership
    user = User(
        email=f"owner-{uuid4().hex[:6]}@dining.com",
        normalized_email=f"owner-{uuid4().hex[:6]}@dining.com",
        display_name="Dining Owner",
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

    # 3. Setup Session & Token
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

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org.id),
    }

    # 4. Create Restaurant (POST /api/v1/restaurants)
    create_payload = {
        "name": "Bistro Central",
        "slug": "bistro-central",
        "timezone": "America/New_York",
    }
    create_res = authed_client.post(
        "/api/v1/restaurants",
        headers=headers,
        json=create_payload,
    )
    assert create_res.status_code == 201
    created_body = create_res.json()
    assert created_body["success"] is True
    assert created_body["data"]["name"] == "Bistro Central"
    assert created_body["data"]["slug"] == "bistro-central"
    restaurant_id = created_body["data"]["id"]

    # 5. Duplicate Slug within same organization -> 409
    dup_res = authed_client.post(
        "/api/v1/restaurants",
        headers=headers,
        json=create_payload,
    )
    assert dup_res.status_code == 409
    dup_body = dup_res.json()
    assert dup_body["success"] is False
    assert dup_body["error"]["code"] == "RESOURCE_CONFLICT"

    # 6. List Restaurants (GET /api/v1/restaurants)
    list_res = authed_client.get(
        "/api/v1/restaurants?page=1&page_size=10",
        headers=headers,
    )
    assert list_res.status_code == 200
    list_body = list_res.json()
    assert list_body["success"] is True
    assert len(list_body["data"]["items"]) >= 1
    assert list_body["data"]["pagination"]["page"] == 1
    assert list_body["data"]["pagination"]["total_items"] >= 1

    # 7. Get Specific Restaurant (GET /api/v1/restaurants/{id})
    get_res = authed_client.get(
        f"/api/v1/restaurants/{restaurant_id}",
        headers=headers,
    )
    assert get_res.status_code == 200
    get_body = get_res.json()
    assert get_body["success"] is True
    assert get_body["data"]["id"] == restaurant_id
    assert get_body["data"]["name"] == "Bistro Central"


@pytest.mark.asyncio
async def test_cross_tenant_restaurant_denied(
    authed_client,
    db_session: AsyncSession,
) -> None:
    settings = get_settings()

    # Org A with restaurant
    org_a = Organization(
        name="Org A",
        slug=f"org-a-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org_a)
    await db_session.flush()

    rest_a = Restaurant(
        organization_id=org_a.id,
        name="Restaurant A",
        slug="rest-a",
        timezone="UTC",
        status=RestaurantStatus.ACTIVE,
    )
    db_session.add(rest_a)
    await db_session.flush()

    # Org B with User B
    org_b = Organization(
        name="Org B",
        slug=f"org-b-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org_b)
    await db_session.flush()

    user_b = User(
        email=f"user-b-{uuid4().hex[:6]}@b.com",
        normalized_email=f"user-b-{uuid4().hex[:6]}@b.com",
        display_name="User B",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user_b)
    await db_session.flush()

    membership_b = OrganizationMembership(
        organization_id=org_b.id,
        user_id=user_b.id,
        role=OrganizationRole.STAFF,
        status=MembershipStatus.ACTIVE,
    )
    db_session.add(membership_b)
    await db_session.flush()

    session_service = SessionService(db_session)
    sess_b, _ = await session_service.create_session(user_id=user_b.id)
    await db_session.commit()

    token_b = create_access_token(
        user_id=user_b.id,
        session_id=sess_b.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )

    headers_b = {
        "Authorization": f"Bearer {token_b}",
        "X-Organization-ID": str(org_b.id),
    }

    # User B attempting to view Restaurant A under Org B context -> 404
    cross_res = authed_client.get(
        f"/api/v1/restaurants/{rest_a.id}",
        headers=headers_b,
    )
    assert cross_res.status_code == 404
    body = cross_res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
