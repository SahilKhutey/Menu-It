"""Tests for sensitive data redaction and structured logging (FCD-11 WP-08)."""

import json
import logging

from menu_it.core.logging import JsonFormatter
from menu_it.platform.observability.redaction import (
    mask_card_number,
    redact_authorization_header,
    redact_data,
    redact_query_params,
)


def test_mask_card_number() -> None:
    assert mask_card_number("4111111111111111") == "4111-********-1111"
    # Too short to be a valid PAN
    assert mask_card_number("12345") == "12345"


def test_redact_authorization_header() -> None:
    bearer = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_token_payload"
    assert redact_authorization_header(bearer) == "Bearer [REDACTED]"
    basic = "Basic dXNlcjpwYXNz"
    assert redact_authorization_header(basic) == "Basic [REDACTED]"
    assert redact_authorization_header("") == ""


def test_redact_query_params() -> None:
    url = "https://api.menu-it.com/v1/checkout?token=abc123secret&restaurant_id=rest-1&apiKey=xyz"
    scrubbed = redact_query_params(url)
    assert "token=%5BREDACTED%5D" in scrubbed or "token=[REDACTED]" in scrubbed
    assert "apiKey=%5BREDACTED%5D" in scrubbed or "apiKey=[REDACTED]" in scrubbed
    assert "restaurant_id=rest-1" in scrubbed


def test_redact_data_nested() -> None:
    payload = {
        "user": {
            "name": "Chef Mario",
            "password": "ClearTextPassword123!",
            "secret_key": "my-secret-key",
        },
        "tokens": ["normal", {"refresh_token": "refresh-token-val"}],
        "safe_field": 42,
    }
    redacted = redact_data(payload)
    assert redacted["user"]["name"] == "Chef Mario"
    assert redacted["user"]["password"] == "[REDACTED]"
    assert redacted["user"]["secret_key"] == "[REDACTED]"
    assert redacted["tokens"][0] == "normal"
    assert redacted["tokens"][1]["refresh_token"] == "[REDACTED]"
    assert redacted["safe_field"] == 42


def test_json_formatter_structured_output() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Sample log message",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-12345"
    record.organization_id = "org-999"

    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["message"] == "Sample log message"
    assert parsed["level"] == "INFO"
    assert parsed["request_id"] == "req-12345"
    assert parsed["organization_id"] == "org-999"
    assert "timestamp" in parsed
