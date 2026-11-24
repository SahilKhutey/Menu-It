"""Unit tests for request ID generation and validation (FCD-07 WP-05)."""

from uuid import UUID

from fastapi import Request

from menu_it.api.dependencies.request_context import get_request_id


def test_request_id_dependency_extraction():
    # When X-Request-ID header is set in state
    scope = {
        "type": "http",
        "headers": [(b"x-request-id", b"11111111-1111-1111-1111-111111111111")],
    }
    request = Request(scope)
    request.state.request_id = "11111111-1111-1111-1111-111111111111"
    assert get_request_id(request) == "11111111-1111-1111-1111-111111111111"


def test_request_id_dependency_fallback_generation():
    # When state has no request_id
    scope = {"type": "http", "headers": []}
    request = Request(scope)
    rid = get_request_id(request)
    assert rid is not None
    # Must be valid UUID
    UUID(rid)
