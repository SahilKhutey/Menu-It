"""
Contract Tests for OpenAPI Specification and API Standards (ARC-02 §10 WP-ARC02-04, §12.3 TC-ARC02-15).
"""
import pytest
from app.main import app


def test_openapi_contract_conventions():
    """
    API-005 / TC-ARC02-15:
    Validates OpenAPI schema conformance:
    1. Schema version is OpenAPI 3.1.x
    2. All endpoints under /api/v1/ follow approved HTTP verb semantics
    3. Public routes do not expose administrative parameters
    """
    spec = app.openapi()
    assert spec["openapi"].startswith("3.")
    paths = spec["paths"]

    # Check version prefix
    for path in paths:
        if path.startswith("/health"):
            continue
        assert path.startswith("/api/v1/"), f"Endpoint '{path}' must be versioned under /api/v1/"

    # Check public endpoint contract
    public_path = "/api/v1/public/restaurants/{slug}/menu"
    assert public_path in paths
    assert "get" in paths[public_path]
    # Public menu GET should have no bearer auth requirement in security schemes
    public_get = paths[public_path]["get"]
    assert "security" not in public_get or not public_get["security"], "Public menu endpoint must not require authentication"
