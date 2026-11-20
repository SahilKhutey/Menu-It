"""
Integration Tests for Request Correlation, Observability, and Health Probes (ARC-03 §11.3, §14.2 & §14.3).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_int_arc03_001_health_live_endpoint(client: AsyncClient):
    """
    BE-ARC03-003 / INT-ARC03-001:
    Liveness probe /health/live returns HTTP 200 indicating process is responsive.
    """
    response = await client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "service" in data


@pytest.mark.asyncio
async def test_int_arc03_001_health_ready_endpoint(client: AsyncClient):
    """
    BE-ARC03-004 / INT-ARC03-001:
    Readiness probe /health/ready inspects database connectivity and returns HTTP 200.
    """
    response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_obs_001_auto_generated_correlation_id(client: AsyncClient):
    """
    OBS-001 / INT-ARC03-008:
    When client does not supply X-Request-ID, the server auto-generates a unique
    traceable correlation ID and returns it in response headers.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"].startswith("req_")
    assert "X-Response-Time" in response.headers


@pytest.mark.asyncio
async def test_obs_001_echoed_correlation_id(client: AsyncClient):
    """
    OBS-001 / INT-ARC03-008:
    When client supplies an X-Request-ID header, the server propagates it
    through the request lifecycle and echoes it back in response headers.
    """
    custom_trace_id = "trace-client-order-987654"
    response = await client.get("/health", headers={"X-Request-ID": custom_trace_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_trace_id


@pytest.mark.asyncio
async def test_obs_002_correlation_id_included_in_error_payload(client: AsyncClient):
    """
    OBS-002 / ARC-03 §6.3:
    When an API error occurs, the RFC 7807 problem details JSON body must include
    the traceable request_id matching response headers.
    """
    custom_trace_id = "trace-err-test-404"
    response = await client.get(
        "/api/v1/public/restaurants/non-existent-restaurant-slug/menu",
        headers={"X-Request-ID": custom_trace_id}
    )
    assert response.status_code == 404
    data = response.json()
    assert data["request_id"] == custom_trace_id
    assert response.headers.get("X-Request-ID") == custom_trace_id
