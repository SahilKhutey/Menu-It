"""Integration tests for API rate limiting infrastructure (FCD-07 WP-10)."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from menu_it.api.exceptions.handlers import register_api_exception_handlers
from menu_it.infrastructure.rate_limiting import (
    InMemoryRateLimiter,
    rate_limit,
)


def test_rate_limiting_integration() -> None:
    test_limiter = InMemoryRateLimiter()
    app = FastAPI()
    register_api_exception_handlers(app)

    @app.get(
        "/api/v1/test/throttled",
        dependencies=[Depends(rate_limit(requests=2, window_seconds=60, limiter=test_limiter))],
    )
    def throttled_endpoint():
        return {"status": "ok"}

    client = TestClient(app)

    # 1st request -> allowed
    res1 = client.get("/api/v1/test/throttled")
    assert res1.status_code == 200
    assert res1.headers.get("X-RateLimit-Limit") == "2"
    assert res1.headers.get("X-RateLimit-Remaining") == "1"

    # 2nd request -> allowed
    res2 = client.get("/api/v1/test/throttled")
    assert res2.status_code == 200
    assert res2.headers.get("X-RateLimit-Limit") == "2"
    assert res2.headers.get("X-RateLimit-Remaining") == "0"

    # 3rd request -> blocked (429)
    res3 = client.get("/api/v1/test/throttled")
    assert res3.status_code == 429
    assert res3.headers.get("Retry-After") is not None
    assert res3.headers.get("X-RateLimit-Remaining") == "0"
    body = res3.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "rate limit exceeded" in body["error"]["message"].lower()
