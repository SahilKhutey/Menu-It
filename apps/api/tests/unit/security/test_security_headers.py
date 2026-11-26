"""Tests for hardened security response headers middleware (FCD-11 WP-05)."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from menu_it.api.middleware.security_headers import SecurityHeadersMiddleware


async def sample_endpoint(request):
    return PlainTextResponse("Hello World")


@pytest.mark.asyncio
async def test_security_headers_middleware_injected() -> None:
    app = Starlette(
        routes=[Route("/test", sample_endpoint)],
        middleware=[],
    )
    app.add_middleware(SecurityHeadersMiddleware, enable_hsts=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/test")
        assert response.status_code == 200

        headers = response.headers
        assert headers["x-content-type-options"] == "nosniff"
        assert headers["x-frame-options"] == "DENY"
        assert headers["referrer-policy"] == "strict-origin-when-cross-origin"
        assert "permissions-policy" in headers
        assert "cross-origin-opener-policy" in headers
        assert "cross-origin-resource-policy" in headers
        assert "content-security-policy" in headers


@pytest.mark.asyncio
async def test_security_headers_hsts_on_https() -> None:
    app = Starlette(
        routes=[Route("/secure", sample_endpoint)],
        middleware=[],
    )
    app.add_middleware(SecurityHeadersMiddleware, enable_hsts=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://testserver") as client:
        response = await client.get("/secure", headers={"x-forwarded-proto": "https"})
        assert response.status_code == 200

        headers = response.headers
        assert "strict-transport-security" in headers
        assert "max-age=" in headers["strict-transport-security"]
