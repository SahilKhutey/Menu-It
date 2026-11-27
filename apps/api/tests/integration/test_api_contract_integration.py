"""API and Frontend Contract Integration Tests (FCD-13 WP-05).

Verifies:
- OpenAPI schema generation and path completeness
- Universal API response envelope conformance
- Standardized error contracts and validation mapping
- Request correlation headers
"""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from menu_it.application import create_application


@pytest.mark.integration
def test_openapi_schema_generation():
    """APIINT-01: FastAPI application generates valid OpenAPI 3.x schema with version and routes."""
    app = create_application()
    schema = app.openapi()

    assert schema is not None
    assert "openapi" in schema
    assert "paths" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "Menu-It API"
    assert schema["info"]["version"] == "0.1.0"

    # Verify foundational path declarations
    paths = schema["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/system/info" in paths
    assert "/api/v1/metrics" in paths


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_response_envelope_and_request_id():
    """FEINT-T09: Responses adhere to envelope standard and preserve valid UUID X-Request-ID."""
    app = create_application()
    transport = ASGITransport(app=app)
    req_id = str(uuid4())

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/v1/health", headers={"X-Request-ID": req_id})
        assert resp.status_code == 200
        assert resp.headers.get("X-Request-ID") == req_id
        assert "X-Response-Time-MS" in resp.headers

        body = resp.json()
        assert isinstance(body, dict)
