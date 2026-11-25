"""Sensitive data redaction utilities (FCD-09 WP-04)."""

from typing import Any

SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "cookie",
        "secret",
        "api_key",
        "client_secret",
        "auth_secret_key",
        "private_key",
        "x-api-key",
        "credential",
    }
)


def redact_mapping(values: dict[str, Any]) -> dict[str, Any]:
    """Recursively redact sensitive credentials, tokens, and secrets from dictionaries."""
    result: dict[str, Any] = {}
    for key, value in values.items():
        normalized = str(key).strip().lower()
        if normalized in SENSITIVE_KEYS:
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = redact_mapping(value)
        elif isinstance(value, list):
            result[key] = [
                redact_mapping(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            result[key] = value
    return result
