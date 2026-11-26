"""Unit tests for structured application logging and redaction (FCD-09 WP-04)."""

import json
import logging

from menu_it.core.logging import (
    JsonFormatter,
    get_context_logger,
)
from menu_it.platform.common.redaction import redact_mapping


def test_redact_mapping_masks_sensitive_keys():
    """Redacts passwords, tokens, API keys, and nested structures."""
    payload = {
        "username": "chef_john",
        "password": "plain_password_123",
        "nested": {
            "token": "bearer_secret_xyz",
            "safe_field": 42,
        },
        "headers": [
            {"authorization": "Bearer 123", "host": "api.menu-it.com"},
            {"cookie": "session=abc", "content-type": "application/json"},
        ],
    }
    redacted = redact_mapping(payload)
    assert redacted["username"] == "chef_john"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["nested"]["token"] == "[REDACTED]"
    assert redacted["nested"]["safe_field"] == 42
    assert redacted["headers"][0]["authorization"] == "[REDACTED]"
    assert redacted["headers"][0]["host"] == "api.menu-it.com"
    assert redacted["headers"][1]["cookie"] == "[REDACTED]"


def test_json_formatter_serializes_structured_record():
    """JsonFormatter formats standard records into valid JSON payloads."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="menu_it.platform.files",
        level=logging.INFO,
        pathname="files.py",
        lineno=42,
        msg="File uploaded successfully",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.organization_id = "org-456"

    output = formatter.format(record)
    parsed = json.loads(output)
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "menu_it.platform.files"
    assert parsed["message"] == "File uploaded successfully"
    assert parsed["request_id"] == "req-123"
    assert parsed["organization_id"] == "org-456"
    assert "timestamp" in parsed


def test_context_logger_adapter_binds_context():
    """ContextLoggerAdapter injects contextual fields into record kwargs."""
    adapter = get_context_logger(
        "test.module",
        request_id="req-999",
        correlation_id="corr-888",
        organization_id="org-777",
    )
    msg, kwargs = adapter.process("Sample event", {})
    assert msg == "Sample event"
    assert kwargs["extra"]["request_id"] == "req-999"
    assert kwargs["extra"]["correlation_id"] == "corr-888"
    assert kwargs["extra"]["organization_id"] == "org-777"
