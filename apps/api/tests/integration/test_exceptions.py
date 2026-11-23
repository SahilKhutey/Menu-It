"""Integration tests for centralized exception handlers."""

from fastapi import HTTPException
from fastapi.testclient import TestClient

from menu_it.application import create_application


def test_http_exception_format():
    """Verify HTTPException returns enveloped RFC 7807/9457 structured JSON."""
    app = create_application()

    @app.get("/test-http-error")
    async def http_error():
        raise HTTPException(
            status_code=404,
            detail="Resource not found.",
        )

    with TestClient(app) as client:
        response = client.get("/test-http-error")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "HTTP_ERROR"
        assert data["error"]["message"] == "Resource not found."
        assert "request_id" in data["meta"]


def test_unexpected_exception_is_sanitized():
    """Verify unhandled exception returns sanitized 500 without leaking details."""
    app = create_application()

    @app.get("/test-server-error")
    async def server_error():
        raise RuntimeError("Private internal diagnostic that must not leak")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test-server-error")
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "Private internal diagnostic" not in str(data)
        assert data["error"]["message"] == "An unexpected server error occurred."
        assert "request_id" in data["meta"]
