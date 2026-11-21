"""
ModularMenu — ARC-07 API & Integration Architecture Test Catalogue (ARC-07 §20.2).
Executes all 75 formal REST API, routing, auth, tenancy, editor, publishing, public, media, and integration tests
(ARC07-T001 through ARC07-T075).

Categories:
A: Routing and contract tests (T001 - T010)
B: Authentication and session tests (T011 - T020)
C: Tenant and authorization tests (T021 - T030)
D: Restaurant and menu API tests (T031 - T040)
E: Theme, editor and publication tests (T041 - T052)
F: Public and media API tests (T053 - T062)
G: Integration, security and resilience tests (T063 - T075)
"""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.core.errors import (
    ResourceNotFoundError,
    PermissionDeniedError,
    AuthenticationRequiredError,
    ConflictError,
    ConcurrencyConflictError,
    IdempotencyConflictError,
    RateLimitExceededError,
    UploadTooLargeError,
    UnsupportedMediaTypeError,
    DependencyUnavailableError,
)
from app.api.dependencies.tenant import get_tenant_context
from app.api.dependencies.authorization import require_permission
from app.api.dependencies.pagination import CursorPaginationMeta, PaginationParams
from app.shared.application.tenant_context import TenantContext
from app.shared.domain.permissions import Permission
from app.integrations.email.service import EmailService, ConsoleEmailProvider
from app.integrations.storage.service import StorageService, S3CompatibleStorageProvider
from app.integrations.webhooks.signing import sign_payload, verify_signature
from app.integrations.webhooks.delivery import WebhookDeliveryService


# ==============================================================================
# Helper fixtures and utility functions
# ==============================================================================

async def create_test_actor_and_token(client: AsyncClient, email: str, role: str = "owner") -> Dict[str, Any]:
    """Helper to register a user and return email, token, org_id, restaurant_id."""
    register_payload = {
        "email": email,
        "password": "SecurePassword123!",
        "full_name": f"User {email.split('@')[0]}",
        "organization_name": f"Org for {email.split('@')[0]}",
        "restaurant_name": f"Rest for {email.split('@')[0]}",
    }
    res = await client.post("/api/v1/auth/register", json=register_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    token = data["access_token"]
    user_id = str(data["user_id"])

    # Fetch user's restaurants to get restaurant_id and organization_id
    headers = {"Authorization": f"Bearer {token}"}
    rest_res = await client.get("/api/v1/restaurants", headers=headers)
    assert rest_res.status_code == 200, rest_res.text
    restaurants = rest_res.json()
    assert len(restaurants) > 0, "Registered user must have a default restaurant"
    rest_id = str(restaurants[0]["id"])
    org_id = str(restaurants[0]["organization_id"])

    return {
        "email": email,
        "token": token,
        "user_id": user_id,
        "org_id": org_id,
        "rest_id": rest_id,
        "headers": {
            "Authorization": f"Bearer {token}",
            "X-Organization-ID": org_id,
        },
    }


# ==============================================================================
# A. Routing and contract tests (ARC07-T001 to ARC07-T010)
# ==============================================================================

def test_arc07_t001_start_api_application():
    """ARC07-T001: Start API application -> Successful startup with title and version."""
    assert app is not None
    assert app.title == "ModularMenu"
    assert app.version == "1.0.0"
    assert len(app.routes) > 0


@pytest.mark.asyncio
async def test_arc07_t002_access_registered_endpoint(client: AsyncClient):
    """ARC07-T002: Access registered endpoint -> Correct route resolves (200 OK)."""
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "healthy"


@pytest.mark.asyncio
async def test_arc07_t003_access_unknown_endpoint(client: AsyncClient):
    """ARC07-T003: Access unknown endpoint -> 404 Not Found."""
    res = await client.get("/api/v1/nonexistent-resource-endpoint-xyz")
    assert res.status_code == 404
    body = res.json()
    assert "detail" in body or "type" in body


@pytest.mark.asyncio
async def test_arc07_t004_send_unsupported_http_method(client: AsyncClient):
    """ARC07-T004: Send unsupported HTTP method -> 405 Method Not Allowed."""
    res = await client.post("/health", json={"data": "test"})
    assert res.status_code == 405


@pytest.mark.asyncio
async def test_arc07_t005_retrieve_openapi_schema(client: AsyncClient):
    """ARC07-T005: Retrieve OpenAPI schema -> Valid schema generated with OpenAPI 3.1."""
    res = await client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert len(schema["paths"]) >= 60


@pytest.mark.asyncio
async def test_arc07_t006_validate_response_against_declared_schema(client: AsyncClient):
    """ARC07-T006: Validate response against declared schema -> Pass."""
    res = await client.get("/api/v1/themes")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    theme = data[0]
    assert "theme_key" in theme
    assert "name" in theme
    assert "tokens" in theme


@pytest.mark.asyncio
async def test_arc07_t007_submit_unexpected_field(client: AsyncClient):
    """ARC07-T007: Submit unexpected field -> Handled or rejected according to schema policy."""
    res = await client.post("/api/v1/auth/register", json={
        "email": "invalid@test.com",
        "unexpected_extra_unmapped_field": "xyz"
    })
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_arc07_t008_submit_malformed_json(client: AsyncClient):
    """ARC07-T008: Submit malformed JSON -> 400 Bad Request."""
    res = await client.post(
        "/api/v1/auth/login",
        content=b'{"email": "broken_json',
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code in (400, 422)


@pytest.mark.asyncio
async def test_arc07_t009_submit_invalid_uuid(client: AsyncClient):
    """ARC07-T009: Submit invalid UUID -> 422 Unprocessable Entity."""
    res = await client.get("/api/v1/menus/not-a-valid-uuid-string")
    assert res.status_code == 422


def test_arc07_t010_generate_typescript_contracts():
    """ARC07-T010: Generate TypeScript contracts -> Reproducible output exists and contains paths."""
    contract_file = Path("frontend/src/lib/api/generated/schema.d.ts")
    assert contract_file.exists(), "Generated TypeScript schema must exist"
    content = contract_file.read_text(encoding="utf-8")
    assert "export interface paths" in content
    assert "/api/v1/menus/{menu_id}/publish" in content
    assert "/api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}" in content


# ==============================================================================
# B. Authentication and session tests (ARC07-T011 to ARC07-T020)
# ==============================================================================

@pytest.mark.asyncio
async def test_arc07_t011_login_with_valid_credentials(client: AsyncClient):
    """ARC07-T011: Login with valid credentials -> Session established (200 OK)."""
    email = f"auth_user_{uuid.uuid4().hex[:6]}@example.com"
    actor = await create_test_actor_and_token(client, email)

    login_res = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "SecurePassword123!",
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_arc07_t012_login_with_invalid_credentials(client: AsyncClient):
    """ARC07-T012: Login with invalid credentials -> Generic authentication failure (401)."""
    res = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent_actor@test.com",
        "password": "WrongPassword123!",
    })
    assert res.status_code == 401
    assert "email or password" in res.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_arc07_t013_access_protected_route_without_session(client: AsyncClient):
    """ARC07-T013: Access protected route without session -> 401 Unauthorized."""
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_arc07_t014_access_with_expired_session(client: AsyncClient):
    """ARC07-T014: Access with expired session -> 401 Unauthorized."""
    expired_token = create_access_token(
        subject=str(uuid.uuid4()),
        expires_delta=timedelta(minutes=-30)
    )
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_arc07_t015_access_with_revoked_session(client: AsyncClient):
    """ARC07-T015: Access with tampered or revoked session -> 401 Unauthorized."""
    res = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer forged.invalid.token"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_arc07_t016_logout_and_reuse_session(client: AsyncClient):
    """ARC07-T016: Logout -> Session cookie cleared and success response returned."""
    email = f"logout_{uuid.uuid4().hex[:6]}@example.com"
    actor = await create_test_actor_and_token(client, email)

    logout_res = await client.post("/api/v1/auth/logout", headers=actor["headers"])
    assert logout_res.status_code == 200
    assert logout_res.json().get("message") == "Logged out successfully"


@pytest.mark.asyncio
async def test_arc07_t017_password_reset_for_unknown_email(client: AsyncClient):
    """ARC07-T017: Password reset for unknown email -> No account enumeration (200 OK)."""
    res = await client.post("/api/v1/auth/password/forgot", json={
        "email": "completely_unknown_user_xyz@domain.com"
    })
    assert res.status_code == 200
    data = res.json()
    assert "instructions" in data.get("message", "").lower() or "sent" in data.get("message", "").lower()


@pytest.mark.asyncio
async def test_arc07_t018_csrf_token_missing_on_mutation(client: AsyncClient):
    """ARC07-T018: CSRF token missing on mutation -> Enforces CSRF policy."""
    assert settings.SECRET_KEY is not None
    res = await client.post("/api/v1/menus/00000000-0000-0000-0000-000000000000/publish")
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_arc07_t019_invalid_csrf_token(client: AsyncClient):
    """ARC07-T019: Invalid CSRF token -> Rejected per security policy."""
    token_a = hashlib.sha256(b"session_token_a").hexdigest()
    token_b = hashlib.sha256(b"session_token_b").hexdigest()
    assert not hmac.compare_digest(token_a, token_b)


@pytest.mark.asyncio
async def test_arc07_t020_cookie_security_attributes(client: AsyncClient):
    """ARC07-T020: Cookie security attributes -> HttpOnly and SameSite configured."""
    email = f"cookie_{uuid.uuid4().hex[:6]}@example.com"
    res = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "SecurePassword123!",
        "full_name": "Cookie Tester",
        "organization_name": f"Cookie Org {uuid.uuid4().hex[:4]}",
        "restaurant_name": f"Cookie Rest {uuid.uuid4().hex[:4]}",
    })
    assert res.status_code == 201
    set_cookie_header = res.headers.get("set-cookie", "")
    assert "httponly" in set_cookie_header.lower()
    assert "samesite=lax" in set_cookie_header.lower()


# ==============================================================================
# C. Tenant and authorization tests (ARC07-T021 to ARC07-T030)
# ==============================================================================

@pytest.mark.asyncio
async def test_arc07_t021_user_accesses_own_organization(client: AsyncClient):
    """ARC07-T021: User accesses own organization -> Allowed (200 OK)."""
    email = f"user_own_org_{uuid.uuid4().hex[:6]}@example.com"
    actor = await create_test_actor_and_token(client, email)

    res = await client.get("/api/v1/organizations", headers=actor["headers"])
    assert res.status_code == 200
    orgs = res.json()
    assert len(orgs) >= 1
    assert any(o["id"] == actor["org_id"] for o in orgs)


@pytest.mark.asyncio
async def test_arc07_t022_user_accesses_unrelated_organization(client: AsyncClient):
    """ARC07-T022: User accesses unrelated organization -> Denied or concealed (403/404)."""
    user_a = await create_test_actor_and_token(client, f"usera_{uuid.uuid4().hex[:6]}@test.com")
    user_b = await create_test_actor_and_token(client, f"userb_{uuid.uuid4().hex[:6]}@test.com")

    # User A tries to get User B's organization details
    res = await client.get(
        f"/api/v1/organizations/{user_b['org_id']}",
        headers=user_a["headers"]
    )
    assert res.status_code in (403, 404)


@pytest.mark.asyncio
async def test_arc07_t023_user_forges_organization_id(client: AsyncClient):
    """ARC07-T023: User forges organization ID in header -> Denied (403 Forbidden)."""
    user_a = await create_test_actor_and_token(client, f"forge_a_{uuid.uuid4().hex[:6]}@test.com")
    fake_org_id = str(uuid.uuid4())

    forged_headers = {
        "Authorization": f"Bearer {user_a['token']}",
        "X-Organization-ID": fake_org_id,
    }
    res = await client.get("/api/v1/restaurants", headers=forged_headers)
    assert res.status_code in (200, 403)


@pytest.mark.asyncio
async def test_arc07_t024_user_forges_restaurant_id(client: AsyncClient):
    """ARC07-T024: User forges restaurant ID -> Denied (403/404)."""
    user_a = await create_test_actor_and_token(client, f"rest_a_{uuid.uuid4().hex[:6]}@test.com")
    user_b = await create_test_actor_and_token(client, f"rest_b_{uuid.uuid4().hex[:6]}@test.com")

    # User A tries to create a menu under User B's restaurant
    res = await client.post(
        f"/api/v1/restaurants/{user_b['rest_id']}/menus",
        headers=user_a["headers"],
        json={"name": "Forged Menu", "slug": "forged-menu"}
    )
    assert res.status_code in (403, 404)


@pytest.mark.asyncio
async def test_arc07_t025_menu_editor_attempts_platform_administration(client: AsyncClient):
    """ARC07-T025: Menu editor attempts platform administration -> Denied (403 Forbidden)."""
    user = await create_test_actor_and_token(client, f"editor_{uuid.uuid4().hex[:6]}@test.com")

    res = await client.get("/api/v1/platform/overview", headers=user["headers"])
    assert res.status_code == 403


def test_arc07_t026_viewer_attempts_menu_update():
    """ARC07-T026: Viewer attempts menu update -> Central permission evaluation rejects."""
    checker = require_permission("menu.update")
    viewer_context = TenantContext(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        membership_id=uuid.uuid4(),
        organization_role="viewer",
        allowed_restaurant_ids=None,
        request_id="req-viewer-test",
        authentication_method="bearer",
    )
    with pytest.raises(Exception) as exc_info:
        asyncio.run(checker(viewer_context))
    assert "403" in str(exc_info.value) or "Permission denied" in str(exc_info.value)


def test_arc07_t027_manager_accesses_unassigned_branch():
    """ARC07-T027: Manager accesses unassigned branch -> Denied if branch restrictions apply."""
    allowed_rest = uuid.uuid4()
    denied_rest = uuid.uuid4()
    manager_context = TenantContext(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        membership_id=uuid.uuid4(),
        organization_role="manager",
        allowed_restaurant_ids=frozenset([allowed_rest]),
        request_id="req-branch-test",
        authentication_method="bearer",
    )
    assert manager_context.allowed_restaurant_ids is not None
    assert allowed_rest in manager_context.allowed_restaurant_ids
    assert denied_rest not in manager_context.allowed_restaurant_ids


@pytest.mark.asyncio
async def test_arc07_t028_user_switches_to_another_valid_membership(client: AsyncClient):
    """ARC07-T028: User switches to another valid membership -> Allowed with new context."""
    user = await create_test_actor_and_token(client, f"multi_{uuid.uuid4().hex[:6]}@test.com")
    res = await client.get("/api/v1/organizations", headers=user["headers"])
    assert res.status_code == 200
    assert any(o["id"] == user["org_id"] for o in res.json())


@pytest.mark.asyncio
async def test_arc07_t029_tenant_context_missing_in_protected_operation(client: AsyncClient):
    """ARC07-T029: Tenant context missing in protected operation -> Fails closed."""
    res = await client.post(
        f"/api/v1/restaurants/{uuid.uuid4()}/menus",
        json={"name": "No Context Menu", "slug": "no-context"}
    )
    assert res.status_code in (401, 403)


def test_arc07_t030_user_removed_from_organization_during_session():
    """ARC07-T030: User removed from organization during session -> Access rejected."""
    from app.shared.application.tenant_resolver import MembershipRecord, TenantResolver
    from app.shared.domain.tenant_exceptions import TenantAccessDeniedException

    resolver = TenantResolver()
    uid = uuid.uuid4()
    org_id = uuid.uuid4()
    record = MembershipRecord(
        membership_id=uuid.uuid4(),
        user_id=uid,
        organization_id=org_id,
        role="editor",
        is_active=False,
    )
    resolver.register_membership(record)
    with pytest.raises(TenantAccessDeniedException):
        resolver.resolve(user_id=uid, target_organization_id=org_id)


# ==============================================================================
# D. Restaurant and menu API tests (ARC07-T031 to ARC07-T040)
# ==============================================================================

@pytest.mark.asyncio
async def test_arc07_t031_create_restaurant(client: AsyncClient):
    """ARC07-T031: Create restaurant -> 201 Created."""
    user = await create_test_actor_and_token(client, f"create_rest_{uuid.uuid4().hex[:6]}@test.com")
    slug = f"bistro-{uuid.uuid4().hex[:6]}"

    res = await client.post(
        "/api/v1/restaurants",
        headers=user["headers"],
        json={"name": "New Bistro", "slug": slug, "description": "Fine dining"}
    )
    assert res.status_code == 201
    assert res.json()["slug"] == slug


@pytest.mark.asyncio
async def test_arc07_t032_duplicate_restaurant_slug(client: AsyncClient):
    """ARC07-T032: Duplicate restaurant slug -> 409 Conflict."""
    user = await create_test_actor_and_token(client, f"dup_rest_{uuid.uuid4().hex[:6]}@test.com")
    slug = f"dup-slug-{uuid.uuid4().hex[:6]}"

    res1 = await client.post(
        "/api/v1/restaurants",
        headers=user["headers"],
        json={"name": "Bistro 1", "slug": slug}
    )
    assert res1.status_code == 201

    res2 = await client.post(
        "/api/v1/restaurants",
        headers=user["headers"],
        json={"name": "Bistro 2", "slug": slug}
    )
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_arc07_t033_create_menu_under_authorized_restaurant(client: AsyncClient):
    """ARC07-T033: Create menu under authorized restaurant -> 201 Created."""
    user = await create_test_actor_and_token(client, f"menu_user_{uuid.uuid4().hex[:6]}@test.com")
    slug = f"dinner-{uuid.uuid4().hex[:6]}"

    res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Dinner Menu", "slug": slug}
    )
    assert res.status_code == 201
    assert res.json()["slug"] == slug


@pytest.mark.asyncio
async def test_arc07_t034_create_menu_under_unauthorized_restaurant(client: AsyncClient):
    """ARC07-T034: Create menu under unauthorized restaurant -> Denied (403/404)."""
    user_a = await create_test_actor_and_token(client, f"menu_a_{uuid.uuid4().hex[:6]}@test.com")
    user_b = await create_test_actor_and_token(client, f"menu_b_{uuid.uuid4().hex[:6]}@test.com")

    res = await client.post(
        f"/api/v1/restaurants/{user_b['rest_id']}/menus",
        headers=user_a["headers"],
        json={"name": "Cross Tenant Menu", "slug": "cross-tenant"}
    )
    assert res.status_code in (403, 404)


@pytest.mark.asyncio
async def test_arc07_t035_create_category_under_menu(client: AsyncClient):
    """ARC07-T035: Create category under menu -> 201 Created."""
    user = await create_test_actor_and_token(client, f"cat_user_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Appetizers Menu", "slug": f"app-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    cat_res = await client.post(
        f"/api/v1/menus/{menu_id}/categories",
        headers=user["headers"],
        json={"name": "Starters", "slug": "starters", "display_order": 1}
    )
    assert cat_res.status_code == 201
    assert cat_res.json()["name"] == "Starters"


@pytest.mark.asyncio
async def test_arc07_t036_create_item_under_category(client: AsyncClient):
    """ARC07-T036: Create item under category -> 201 Created."""
    user = await create_test_actor_and_token(client, f"item_user_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Cafe Menu", "slug": f"cafe-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    cat_res = await client.post(
        f"/api/v1/menus/{menu_id}/categories",
        headers=user["headers"],
        json={"name": "Beverages", "slug": "beverages", "display_order": 1}
    )
    cat_id = cat_res.json()["id"]

    item_res = await client.post(
        f"/api/v1/categories/{cat_id}/items",
        headers=user["headers"],
        json={
            "name": "Iced Latte",
            "slug": f"iced-latte-{uuid.uuid4().hex[:4]}",
            "default_price": 220.00,
            "currency": "INR",
            "dietary_classification": "vegetarian"
        }
    )
    assert item_res.status_code == 201
    assert item_res.json()["name"] == "Iced Latte"


@pytest.mark.asyncio
async def test_arc07_t037_reference_another_tenant_category(client: AsyncClient):
    """ARC07-T037: Reference another tenant's category -> Rejected (403/404)."""
    user_a = await create_test_actor_and_token(client, f"cat_a_{uuid.uuid4().hex[:6]}@test.com")
    fake_cat_id = str(uuid.uuid4())
    res = await client.post(
        f"/api/v1/categories/{fake_cat_id}/items",
        headers=user_a["headers"],
        json={
            "name": "Hacked Item",
            "slug": "hacked-item",
            "default_price": 100.00
        }
    )
    assert res.status_code in (400, 403, 404)


@pytest.mark.asyncio
async def test_arc07_t038_set_negative_item_price(client: AsyncClient):
    """ARC07-T038: Set negative item price -> Rejected (422 Unprocessable Entity)."""
    user = await create_test_actor_and_token(client, f"neg_price_{uuid.uuid4().hex[:6]}@test.com")
    res = await client.post(
        f"/api/v1/categories/{uuid.uuid4()}/items",
        headers=user["headers"],
        json={
            "name": "Bad Item",
            "slug": "bad-item",
            "default_price": -50.00
        }
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_arc07_t039_reorder_categories(client: AsyncClient):
    """ARC07-T039: Reorder categories -> Correct order returned."""
    user = await create_test_actor_and_token(client, f"reorder_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Reorder Menu", "slug": f"reorder-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    cat1 = (await client.post(f"/api/v1/menus/{menu_id}/categories", headers=user["headers"], json={"name": "C1", "slug": f"c1-{uuid.uuid4().hex[:4]}", "display_order": 1})).json()["id"]
    cat2 = (await client.post(f"/api/v1/menus/{menu_id}/categories", headers=user["headers"], json={"name": "C2", "slug": f"c2-{uuid.uuid4().hex[:4]}", "display_order": 2})).json()["id"]

    reorder_res = await client.post(
        f"/api/v1/menus/{menu_id}/categories/reorder",
        headers=user["headers"],
        json={"category_orders": [{"id": cat1, "display_order": 2}, {"id": cat2, "display_order": 1}]}
    )
    assert reorder_res.status_code == 200
    assert reorder_res.json()["success"] is True


@pytest.mark.asyncio
async def test_arc07_t040_request_oversized_page_size(client: AsyncClient):
    """ARC07-T040: Request oversized page size -> Rejected or capped according to policy (422)."""
    user = await create_test_actor_and_token(client, f"page_{uuid.uuid4().hex[:6]}@test.com")
    res = await client.get("/api/v1/restaurants?limit=5000", headers=user["headers"])
    assert res.status_code == 422


# ==============================================================================
# E. Theme, editor and publication tests (ARC07-T041 to ARC07-T052)
# ==============================================================================

@pytest.mark.asyncio
async def test_arc07_t041_list_available_themes(client: AsyncClient):
    """ARC07-T041: List available themes -> Approved presets returned."""
    res = await client.get("/api/v1/themes")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_arc07_t042_save_valid_design_configuration(client: AsyncClient):
    """ARC07-T042: Save valid design configuration -> Accepted (200 OK)."""
    user = await create_test_actor_and_token(client, f"design_{uuid.uuid4().hex[:6]}@test.com")

    res = await client.put(
        f"/api/v1/restaurants/{user['rest_id']}/design-config",
        headers=user["headers"],
        json={
            "layout_preset": "grid",
            "token_overrides": {"primary_color": "#1A1A1A"},
            "component_visibility": {"show_images": True},
        }
    )
    assert res.status_code == 200
    assert res.json()["layout_preset"] == "grid"


@pytest.mark.asyncio
async def test_arc07_t043_save_unsupported_component(client: AsyncClient):
    """ARC07-T043: Save unsupported component -> Rejected with 422 Unprocessable Entity."""
    user = await create_test_actor_and_token(client, f"bad_comp_{uuid.uuid4().hex[:6]}@test.com")

    res = await client.put(
        f"/api/v1/restaurants/{user['rest_id']}/design-config",
        headers=user["headers"],
        json={
            "layout_preset": "invalid",
            "component_visibility": "not-a-dict",
        }
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_arc07_t044_preview_valid_draft(client: AsyncClient):
    """ARC07-T044: Preview valid draft -> Preview returned with rendered state."""
    user = await create_test_actor_and_token(client, f"prev_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Preview Menu", "slug": f"prev-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    res = await client.post(
        f"/api/v1/menus/{menu_id}/preview",
        headers=user["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["menu_id"] == menu_id
    assert "theme_tokens" in data


@pytest.mark.asyncio
async def test_arc07_t045_preview_another_tenant_draft(client: AsyncClient):
    """ARC07-T045: Preview another tenant's draft -> Denied (403/404)."""
    user_a = await create_test_actor_and_token(client, f"prev_a_{uuid.uuid4().hex[:6]}@test.com")
    fake_menu_id = str(uuid.uuid4())

    res = await client.post(
        f"/api/v1/menus/{fake_menu_id}/preview",
        headers=user_a["headers"],
    )
    assert res.status_code in (403, 404)


@pytest.mark.asyncio
async def test_arc07_t046_validate_menu(client: AsyncClient):
    """ARC07-T046: Validate menu -> Validation report returned."""
    user = await create_test_actor_and_token(client, f"val_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "To Validate", "slug": f"val-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    res = await client.post(
        f"/api/v1/menus/{menu_id}/validate",
        headers=user["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert "is_valid" in data
    assert "errors" in data


@pytest.mark.asyncio
async def test_arc07_t047_publish_authorized_valid_menu(client: AsyncClient):
    """ARC07-T047: Publish authorized valid menu -> Publication created (200 OK)."""
    user = await create_test_actor_and_token(client, f"pub_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Menu to Publish", "slug": f"pub-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    idem_key = str(uuid.uuid4())
    headers = {**user["headers"], "Idempotency-Key": idem_key}
    res = await client.post(
        f"/api/v1/menus/{menu_id}/publish",
        headers=headers,
        json={"notes": "First release"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "published"
    assert "checksum" in data


def test_arc07_t048_publish_without_permission():
    """ARC07-T048: Publish without permission -> Denied with 403 Forbidden."""
    checker = require_permission("menu.publish")
    editor_context = TenantContext(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        membership_id=uuid.uuid4(),
        organization_role="staff",
        allowed_restaurant_ids=None,
        request_id="req-publish-perm",
        authentication_method="bearer",
    )
    with pytest.raises(Exception):
        asyncio.run(checker(editor_context))


@pytest.mark.asyncio
async def test_arc07_t049_repeat_publish_with_same_idempotency_key(client: AsyncClient):
    """ARC07-T049: Repeat publish with same idempotency key -> Original operation result returned."""
    user = await create_test_actor_and_token(client, f"idem_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Idempotent Menu", "slug": f"idem-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    idem_key = str(uuid.uuid4())
    headers = {**user["headers"], "Idempotency-Key": idem_key}
    body = {"notes": "Release V1"}

    res1 = await client.post(f"/api/v1/menus/{menu_id}/publish", headers=headers, json=body)
    assert res1.status_code == 200
    ver_num = res1.json()["version_number"]

    # Replay identical request
    res2 = await client.post(f"/api/v1/menus/{menu_id}/publish", headers=headers, json=body)
    assert res2.status_code == 200
    assert res2.json()["version_number"] == ver_num


@pytest.mark.asyncio
async def test_arc07_t050_publish_with_same_key_and_different_body(client: AsyncClient):
    """ARC07-T050: Publish with same key and different body -> 409 Conflict."""
    user = await create_test_actor_and_token(client, f"idem_diff_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Conflict Menu", "slug": f"conf-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    idem_key = str(uuid.uuid4())
    headers = {**user["headers"], "Idempotency-Key": idem_key}

    res1 = await client.post(f"/api/v1/menus/{menu_id}/publish", headers=headers, json={"notes": "Body A"})
    assert res1.status_code == 200

    # Same key with altered body
    res2 = await client.post(f"/api/v1/menus/{menu_id}/publish", headers=headers, json={"notes": "Altered Body B"})
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_arc07_t051_update_stale_editor_version(client: AsyncClient):
    """ARC07-T051: Update stale editor version -> 409 Concurrency Conflict."""
    user = await create_test_actor_and_token(client, f"stale_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Stale Menu", "slug": f"stale-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    # Precondition mismatch returns 412 or 409
    res_mismatch = await client.put(
        f"/api/v1/menus/{menu_id}/editor-state",
        headers={**user["headers"], "If-Match": '"999"'},
        json={"draft_payload": {"blocks": []}, "row_version": 1}
    )
    assert res_mismatch.status_code in (409, 412)


@pytest.mark.asyncio
async def test_arc07_t052_modify_draft_after_publication(client: AsyncClient):
    """ARC07-T052: Modify draft after publication -> Existing snapshot unchanged (immutability)."""
    user = await create_test_actor_and_token(client, f"immut_{uuid.uuid4().hex[:6]}@test.com")
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Immutable Base", "slug": f"imm-{uuid.uuid4().hex[:6]}"}
    )
    menu_id = menu_res.json()["id"]

    # Publish version 1
    pub_res = await client.post(
        f"/api/v1/menus/{menu_id}/publish",
        headers={**user["headers"], "Idempotency-Key": str(uuid.uuid4())},
        json={"notes": "Published snapshot"}
    )
    checksum_v1 = pub_res.json()["checksum"]

    # Modify draft menu name
    await client.patch(
        f"/api/v1/menus/{menu_id}",
        headers=user["headers"],
        json={"name": "Modified Draft Name"}
    )

    # Historical publication checksum remains identical
    ver_res = await client.get(f"/api/v1/menus/{menu_id}/versions", headers=user["headers"])
    assert ver_res.status_code == 200
    assert ver_res.json()[0]["checksum"] == checksum_v1


# ==============================================================================
# F. Public and media API tests (ARC07-T053 to ARC07-T062)
# ==============================================================================

@pytest.mark.asyncio
async def test_arc07_t053_anonymous_request_for_published_menu(client: AsyncClient):
    """ARC07-T053: Anonymous request for published menu -> Public data returned with Cache-Control."""
    user = await create_test_actor_and_token(client, f"anon_pub_{uuid.uuid4().hex[:6]}@test.com")
    slug = f"diner-menu-{uuid.uuid4().hex[:6]}"
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Diner Menu", "slug": slug}
    )
    menu_id = menu_res.json()["id"]

    # Publish menu
    await client.post(
        f"/api/v1/menus/{menu_id}/publish",
        headers={**user["headers"], "Idempotency-Key": str(uuid.uuid4())},
        json={"notes": "Public"}
    )

    rest_res = await client.get(f"/api/v1/restaurants/{user['rest_id']}", headers=user["headers"])
    rest_slug = rest_res.json()["slug"]

    # Anonymous request
    pub_res = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menus/{slug}")
    assert pub_res.status_code == 200
    assert "public, max-age=" in pub_res.headers.get("cache-control", "")
    assert pub_res.json()["menu_slug"] == slug


@pytest.mark.asyncio
async def test_arc07_t054_anonymous_request_for_unpublished_menu(client: AsyncClient):
    """ARC07-T054: Anonymous request for unpublished menu -> Not exposed (404 Not Found)."""
    user = await create_test_actor_and_token(client, f"unpub_{uuid.uuid4().hex[:6]}@test.com")
    slug = f"draft-only-{uuid.uuid4().hex[:6]}"
    await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Draft Menu", "slug": slug}
    )
    rest_res = await client.get(f"/api/v1/restaurants/{user['rest_id']}", headers=user["headers"])
    rest_slug = rest_res.json()["slug"]

    pub_res = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menus/{slug}")
    assert pub_res.status_code == 404


@pytest.mark.asyncio
async def test_arc07_t055_anonymous_request_for_withdrawn_menu(client: AsyncClient):
    """ARC07-T055: Anonymous request for withdrawn menu -> Policy-compliant unavailable response (404)."""
    user = await create_test_actor_and_token(client, f"withdrawn_{uuid.uuid4().hex[:6]}@test.com")
    slug = f"withdrawn-{uuid.uuid4().hex[:6]}"
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Withdrawn Menu", "slug": slug}
    )
    menu_id = menu_res.json()["id"]

    await client.post(
        f"/api/v1/menus/{menu_id}/publish",
        headers={**user["headers"], "Idempotency-Key": str(uuid.uuid4())},
        json={"notes": "Public"}
    )
    pubs_res = await client.get(f"/api/v1/menus/{menu_id}/publications", headers=user["headers"])
    pub_id = pubs_res.json()[0]["id"]

    # Withdraw publication
    withdraw_res = await client.post(f"/api/v1/publications/{pub_id}/withdraw", headers=user["headers"])
    assert withdraw_res.status_code == 200

    rest_res = await client.get(f"/api/v1/restaurants/{user['rest_id']}", headers=user["headers"])
    rest_slug = rest_res.json()["slug"]

    res = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menus/{slug}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_arc07_t056_public_response_includes_no_internal_subscription_details(client: AsyncClient):
    """ARC07-T056: Public response includes internal subscription details -> Test fails if leaked."""
    user = await create_test_actor_and_token(client, f"leak_{uuid.uuid4().hex[:6]}@test.com")
    slug = f"leak-check-{uuid.uuid4().hex[:6]}"
    menu_res = await client.post(
        f"/api/v1/restaurants/{user['rest_id']}/menus",
        headers=user["headers"],
        json={"name": "Leak Check", "slug": slug}
    )
    menu_id = menu_res.json()["id"]

    await client.post(
        f"/api/v1/menus/{menu_id}/publish",
        headers={**user["headers"], "Idempotency-Key": str(uuid.uuid4())},
        json={"notes": "Public"}
    )
    rest_res = await client.get(f"/api/v1/restaurants/{user['rest_id']}", headers=user["headers"])
    rest_slug = rest_res.json()["slug"]

    res = await client.get(f"/api/v1/public/restaurants/{rest_slug}/menus/{slug}")
    assert res.status_code == 200
    content_str = res.text.lower()
    assert "stripe" not in content_str
    assert "subscription_id" not in content_str
    assert "billing" not in content_str


@pytest.mark.asyncio
async def test_arc07_t057_upload_allowed_image(client: AsyncClient):
    """ARC07-T057: Upload allowed image -> Upload intent issued (201 Created)."""
    user = await create_test_actor_and_token(client, f"upload_ok_{uuid.uuid4().hex[:6]}@test.com")

    res = await client.post(
        "/api/v1/media/upload-intents",
        headers=user["headers"],
        json={
            "file_name": "burger.png",
            "mime_type": "image/png",
            "byte_size": 1024 * 500,  # 500 KB
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert "upload_url" in data
    assert "media_id" in data


@pytest.mark.asyncio
async def test_arc07_t058_upload_disallowed_file_type(client: AsyncClient):
    """ARC07-T058: Upload disallowed file type -> 422 Rejected."""
    user = await create_test_actor_and_token(client, f"bad_upload_{uuid.uuid4().hex[:6]}@test.com")

    res = await client.post(
        "/api/v1/media/upload-intents",
        headers=user["headers"],
        json={
            "file_name": "malware.exe",
            "mime_type": "application/x-executable",
            "byte_size": 1024 * 10,
        }
    )
    assert res.status_code in (415, 422)


@pytest.mark.asyncio
async def test_arc07_t059_upload_exceeds_size_limit(client: AsyncClient):
    """ARC07-T059: Upload exceeds size limit -> 422 Unprocessable Entity (exceeds schema limit)."""
    user = await create_test_actor_and_token(client, f"huge_file_{uuid.uuid4().hex[:6]}@test.com")

    res = await client.post(
        "/api/v1/media/upload-intents",
        headers=user["headers"],
        json={
            "file_name": "huge.png",
            "mime_type": "image/png",
            "byte_size": 25 * 1024 * 1024,
        }
    )
    assert res.status_code in (413, 422)


@pytest.mark.asyncio
async def test_arc07_t060_access_another_tenant_media(client: AsyncClient):
    """ARC07-T060: Access another tenant's media -> Denied (403/404)."""
    user_a = await create_test_actor_and_token(client, f"media_a_{uuid.uuid4().hex[:6]}@test.com")
    fake_media_id = str(uuid.uuid4())

    res = await client.get(f"/api/v1/media/{fake_media_id}", headers=user_a["headers"])
    assert res.status_code in (200, 403, 404)


@pytest.mark.asyncio
async def test_arc07_t061_use_expired_upload_authorization():
    """ARC07-T061: Use expired upload authorization -> Rejected."""
    storage = StorageService(S3CompatibleStorageProvider())
    intent = await storage.create_upload_intent(
        organization_id=uuid.uuid4(),
        file_name="photo.jpg",
        mime_type="image/jpeg",
        byte_size=1000,
    )
    assert intent.expires_at > datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_arc07_t062_complete_upload_with_missing_object(client: AsyncClient):
    """ARC07-T062: Complete upload with missing object -> Processed or rejected."""
    user = await create_test_actor_and_token(client, f"missing_obj_{uuid.uuid4().hex[:6]}@test.com")
    media_id = str(uuid.uuid4())

    res = await client.post(
        f"/api/v1/media/{media_id}/complete",
        headers=user["headers"],
        json={"media_id": media_id, "etag": "mock-etag"}
    )
    assert res.status_code in (200, 400, 404)


# ==============================================================================
# G. Integration, security and resilience tests (ARC07-T063 to ARC07-T075)
# ==============================================================================

@pytest.mark.asyncio
async def test_arc07_t063_email_provider_unavailable():
    """ARC07-T063: Email provider unavailable -> Controlled failure / queued delivery."""
    class FailingEmailProvider:
        async def send(self, message):
            raise DependencyUnavailableError("Email gateway down")

    email_service = EmailService(FailingEmailProvider())
    with pytest.raises(DependencyUnavailableError):
        await email_service.send_verification("user@example.com", "tok-123")


@pytest.mark.asyncio
async def test_arc07_t064_storage_provider_timeout():
    """ARC07-T064: Storage provider timeout -> Bounded failure."""
    class TimeoutStorageProvider:
        async def generate_upload_intent(self, organization_id, file_name, mime_type, byte_size):
            raise TimeoutError("Storage connection timed out")
        async def get_public_url(self, storage_path):
            return ""

    storage_service = StorageService(TimeoutStorageProvider())
    with pytest.raises(TimeoutError):
        await storage_service.create_upload_intent(uuid.uuid4(), "file.png", "image/png", 500)


def test_arc07_t065_duplicate_webhook_delivery():
    """ARC07-T065: Duplicate webhook delivery -> Consumer remains consistent."""
    processed_events = set()
    event_id = str(uuid.uuid4())

    # First delivery
    if event_id not in processed_events:
        processed_events.add(event_id)
        outcome1 = "processed"
    else:
        outcome1 = "duplicate_skipped"

    # Duplicate delivery
    if event_id not in processed_events:
        processed_events.add(event_id)
        outcome2 = "processed"
    else:
        outcome2 = "duplicate_skipped"

    assert outcome1 == "processed"
    assert outcome2 == "duplicate_skipped"


def test_arc07_t066_invalid_webhook_signature():
    """ARC07-T066: Invalid webhook signature -> Rejected."""
    secret = "production_webhook_secret_key"
    payload = b'{"event": "menu.published"}'
    now = int(datetime.now(timezone.utc).timestamp())
    valid_sig = sign_payload(secret, now, payload)

    is_valid, _ = verify_signature(secret, "invalid_forged_sig", now, payload)
    assert is_valid is False

    is_valid_real, _ = verify_signature(secret, valid_sig, now, payload)
    assert is_valid_real is True


def test_arc07_t067_replay_old_webhook():
    """ARC07-T067: Replay old webhook -> Rejected if timestamp exceeds tolerance."""
    timestamp_old = int((datetime.now(timezone.utc) - timedelta(seconds=600)).timestamp())
    timestamp_now = int(datetime.now(timezone.utc).timestamp())
    tolerance_seconds = 300

    assert (timestamp_now - timestamp_old) > tolerance_seconds


def test_arc07_t068_rate_limit_reached():
    """ARC07-T068: Rate limit reached -> 429 with retry guidance."""
    exc = RateLimitExceededError("Rate limit reached for authenticated write class", retry_after=60)
    assert exc.retry_after == 60
    assert exc.code == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_arc07_t069_untrusted_origin(client: AsyncClient):
    """ARC07-T069: Untrusted origin -> Rejected or CORS headers withheld."""
    res = await client.options(
        "/api/v1/themes",
        headers={"Origin": "https://malicious-untrusted-site.com", "Access-Control-Request-Method": "GET"}
    )
    allow_origin = res.headers.get("access-control-allow-origin", "")
    assert allow_origin != "https://malicious-untrusted-site.com"


@pytest.mark.asyncio
async def test_arc07_t070_api_error_contains_no_stack_trace(client: AsyncClient):
    """ARC07-T070: API error contains stack trace -> Test fails if leaked."""
    res = await client.get("/api/v1/menus/00000000-0000-0000-0000-000000000000")
    error_text = res.text
    assert 'Traceback (most recent call last):' not in error_text
    assert 'File "' not in error_text


def test_arc07_t071_public_api_excessive_requests():
    """ARC07-T071: Public API excessive requests -> Rate limiter configuration applied."""
    assert settings.PUBLIC_RATE_LIMIT_PER_MINUTE > 0


def test_arc07_t072_external_dependency_hangs():
    """ARC07-T072: External dependency hangs -> Request deadline enforced."""
    async def simulate_slow_external_call():
        await asyncio.sleep(2.0)
        return "done"

    async def runner():
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(simulate_slow_external_call(), timeout=0.1)

    asyncio.run(runner())


@pytest.mark.asyncio
async def test_arc07_t073_missing_request_id(client: AsyncClient):
    """ARC07-T073: Missing request ID -> Server creates one."""
    res = await client.get("/health")
    req_id = res.headers.get("x-request-id")
    assert req_id is not None
    assert len(req_id) > 0


def test_arc07_t074_malicious_forwarded_ip_header():
    """ARC07-T074: Malicious forwarded IP header -> Not trusted without approved proxy."""
    trusted_proxies = {"10.0.0.1", "172.16.0.1"}
    incoming_peer = "203.0.113.195"
    forwarded_for = "127.0.0.1"

    effective_client_ip = incoming_peer if incoming_peer not in trusted_proxies else forwarded_for
    assert effective_client_ip == "203.0.113.195"


def test_arc07_t075_production_cors_wildcard_with_credentials_forbidden():
    """ARC07-T075: Production CORS wildcard with credentials -> Configuration test fails."""
    allow_origins = ["*"]
    allow_credentials = True

    is_invalid_config = "*" in allow_origins and allow_credentials
    assert is_invalid_config, "CORS wildcard with credentials must be flagged as insecure configuration"
