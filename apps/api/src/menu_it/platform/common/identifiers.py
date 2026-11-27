"""Identifier generation and validation utilities (FCD-09 WP-06)."""

from uuid import UUID, uuid4


def new_uuid() -> UUID:
    """Generate a new cryptographically random UUID v4."""
    return uuid4()


def parse_uuid(value: str | UUID) -> UUID:
    """Parse and validate a UUID value, raising ValueError on malformed inputs."""
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value).strip())
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Invalid UUID format.") from exc
