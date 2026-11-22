"""
Media Management Domain Entities (ARC-04 §6.14, MOD-14).
"""

from dataclasses import dataclass
from uuid import UUID

MAX_MEDIA_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit
ALLOWED_MIME_TYPES = {"image/webp", "image/png", "image/jpeg"}


@dataclass
class MediaAsset:
    asset_id: UUID
    restaurant_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    reference_count: int = 0

    def __post_init__(self) -> None:
        if self.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(f"Unsupported media content type: '{self.content_type}'")
        if self.size_bytes > MAX_MEDIA_SIZE_BYTES:
            raise ValueError(
                f"Media file size {self.size_bytes} exceeds limit of {MAX_MEDIA_SIZE_BYTES} bytes"
            )
        if not self.filename or not self.filename.strip():
            raise ValueError("Media filename is required")

    def increment_references(self) -> None:
        self.reference_count += 1

    def decrement_references(self) -> None:
        if self.reference_count > 0:
            self.reference_count -= 1

    def assert_can_delete(self) -> None:
        if self.reference_count > 0:
            raise ValueError("Cannot delete media asset actively referenced by menu items")
