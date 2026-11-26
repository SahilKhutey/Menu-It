"""Storage key generation utilities (FCD-09 WP-02)."""

from uuid import UUID, uuid4


def build_storage_key(
    *,
    organization_id: UUID | None,
    file_id: UUID,
    extension: str,
) -> str:
    """Build a non-predictable, partitioned internal storage key."""
    if not extension.startswith("."):
        raise ValueError("Extension must start with a dot.")

    ext = extension.lower().strip()
    random_entropy = uuid4().hex
    prefix = f"organizations/{organization_id}" if organization_id else "platform"
    return f"{prefix}/files/{file_id}/{random_entropy}{ext}"
