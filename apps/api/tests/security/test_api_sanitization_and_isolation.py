"""Security tests for API response sanitization and tenant isolation (FCD-07 WP-15)."""

from fastapi.testclient import TestClient


def test_validation_error_does_not_leak_raw_sensitive_input(client: TestClient) -> None:
    # Attempt login with malformed or sensitive payload
    sensitive_token = "SUPER_SECRET_VALUE_DO_NOT_LEAK_IN_RESPONSE"
    payload = {
        "email": "not-an-email",
        "password": sensitive_token,
    }
    res = client.post("/api/v1/auth/login", json=payload)
    # Status should be 422 or 400
    assert res.status_code in (400, 422)
    response_text = res.text
    # Sensitive password string must not be reflected back in error response
    assert sensitive_token not in response_text
