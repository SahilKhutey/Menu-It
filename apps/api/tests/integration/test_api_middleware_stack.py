"""Integration tests for FCD-07 API middleware stack."""

from uuid import UUID

from fastapi.testclient import TestClient


def test_request_id_middleware(client: TestClient) -> None:
    # 1. Without header -> generated UUID
    res = client.get("/api/v1/health/live")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers
    rid = res.headers["X-Request-ID"]
    UUID(rid)

    # 2. With valid UUID -> preserved
    valid_uuid = "12345678-1234-5678-1234-567812345678"
    res2 = client.get("/api/v1/health/live", headers={"X-Request-ID": valid_uuid})
    assert res2.headers["X-Request-ID"] == valid_uuid

    # 3. With invalid string -> replaced with valid UUID
    res3 = client.get("/api/v1/health/live", headers={"X-Request-ID": "invalid-uuid-format"})
    assert res3.headers["X-Request-ID"] != "invalid-uuid-format"
    UUID(res3.headers["X-Request-ID"])


def test_timing_middleware(client: TestClient) -> None:
    res = client.get("/api/v1/health/live")
    assert res.status_code == 200
    assert "X-Response-Time-MS" in res.headers
    timing = float(res.headers["X-Response-Time-MS"])
    assert timing >= 0.0


def test_security_headers_middleware(client: TestClient) -> None:
    res = client.get("/api/v1/health/live")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
