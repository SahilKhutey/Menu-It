"""Integration tests for platform file API endpoints (FCD-09 WP-02)."""

import io
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

PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 30


@pytest.mark.asyncio
async def test_file_api_upload_metadata_content_delete_lifecycle(
    authed_client,
    db_session: AsyncSession,
) -> None:
    settings = get_settings()

    # 1. Setup Tenant Organization A
    org_a = Organization(
        name="Org Alpha",
        slug=f"org-alpha-{uuid4().hex[:6]}",
        status=OrganizationStatus.ACTIVE,
    )
    db_session.add(org_a)
    await db_session.flush()

    user_a = User(
        email=f"user-{uuid4().hex[:6]}@alpha.com",
        normalized_email=f"user-{uuid4().hex[:6]}@alpha.com",
        display_name="Alpha User",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    db_session.add(user_a)
    await db_session.flush()

    db_session.add(
        OrganizationMembership(
            organization_id=org_a.id,
            user_id=user_a.id,
            role=OrganizationRole.ADMIN,
            status=MembershipStatus.ACTIVE,
        )
    )
    session_service = SessionService(db_session)
    sess, _ = await session_service.create_session(user_id=user_a.id)
    await db_session.commit()

    token_a = create_access_token(
        user_id=user_a.id,
        session_id=sess.id,
        signing_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        ttl_seconds=900,
    )
    headers_a = {
        "Authorization": f"Bearer {token_a}",
        "X-Organization-ID": str(org_a.id),
    }

    # 2. Upload tenant-private PNG file
    upload_res = authed_client.post(
        "/api/v1/files",
        headers=headers_a,
        files={"file": ("logo.png", io.BytesIO(PNG_MAGIC), "image/png")},
        data={"visibility": "tenant_private"},
    )
    assert upload_res.status_code == 201
    file_data = upload_res.json()["data"]
    file_id = file_data["id"]
    assert file_data["filename"] == "logo.png"
    assert file_data["mime_type"] == "image/png"
    assert file_data["visibility"] == "tenant_private"

    # 3. Retrieve metadata
    meta_res = authed_client.get(f"/api/v1/files/{file_id}", headers=headers_a)
    assert meta_res.status_code == 200
    assert meta_res.json()["data"]["id"] == file_id

    # 4. Download content stream
    content_res = authed_client.get(f"/api/v1/files/{file_id}/content", headers=headers_a)
    assert content_res.status_code == 200
    assert content_res.content == PNG_MAGIC
    assert content_res.headers["content-type"] == "image/png"

    # 5. Delete file
    delete_res = authed_client.delete(f"/api/v1/files/{file_id}", headers=headers_a)
    assert delete_res.status_code == 200
    assert delete_res.json()["data"]["status"] == "deleted"

    # 6. Verify 404 after deletion
    meta_after = authed_client.get(f"/api/v1/files/{file_id}", headers=headers_a)
    assert meta_after.status_code == 404
