"""Comprehensive sensitive data masking, sanitization, and redaction (FCD-11 WP-08)."""

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SENSITIVE_FIELD_NAMES: frozenset[str] = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "secret_key",
        "auth_secret_key",
        "private_key",
        "token",
        "access_token",
        "refresh_token",
        "id_token",
        "authorization",
        "cookie",
        "api_key",
        "apikey",
        "client_secret",
        "card_number",
        "pan",
        "cvv",
        "cvc",
        "ssn",
        "pin",
    }
)

CARD_PATTERN: re.Pattern = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
BEARER_PATTERN: re.Pattern = re.compile(r"Bearer\s+([A-Za-z0-9\-._~+/]+=*)", re.IGNORECASE)


def mask_card_number(value: str) -> str:
    """Mask credit card PAN retaining only first 4 and last 4 digits."""
    digits = re.sub(r"\D", "", value)
    if len(digits) < 13 or len(digits) > 19:
        return value
    return f"{digits[:4]}-{'*' * (len(digits) - 8)}-{digits[-4:]}"


def redact_authorization_header(header_value: str | None) -> str:
    """Mask bearer or token values in Authorization headers."""
    if not header_value:
        return ""
    if BEARER_PATTERN.search(header_value):
        return BEARER_PATTERN.sub("Bearer [REDACTED]", header_value)
    if header_value.lower().startswith("basic "):
        return "Basic [REDACTED]"
    return "[REDACTED]"


def redact_query_params(url_str: str) -> str:
    """Scrub sensitive credentials and tokens from query strings in URLs."""
    if not url_str or "?" not in url_str:
        return url_str

    try:
        parts = urlsplit(url_str)
        query_params = parse_qsl(parts.query, keep_blank_values=True)
        scrubbed = []
        for key, val in query_params:
            if key.lower() in SENSITIVE_FIELD_NAMES:
                scrubbed.append((key, "[REDACTED]"))
            else:
                scrubbed.append((key, val))
        new_query = urlencode(scrubbed)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    except Exception:
        return url_str


def redact_data(data: Any) -> Any:
    """Recursively redact dictionaries, lists, and strings containing sensitive values."""
    if isinstance(data, dict):
        result: dict[str, Any] = {}
        for key, val in data.items():
            k_lower = str(key).strip().lower()
            if k_lower in SENSITIVE_FIELD_NAMES:
                result[key] = "[REDACTED]"
            elif isinstance(val, (dict, list)):
                result[key] = redact_data(val)
            elif isinstance(val, str) and k_lower == "authorization":
                result[key] = redact_authorization_header(val)
            else:
                result[key] = val
        return result
    elif isinstance(data, list):
        return [redact_data(item) for item in data]
    elif isinstance(data, str):
        # Mask embedded PANs if detected
        return CARD_PATTERN.sub(lambda m: mask_card_number(m.group(0)), data)
    return data
