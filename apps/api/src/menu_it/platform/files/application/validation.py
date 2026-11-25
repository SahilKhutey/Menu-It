"""File validation and magic-byte sniffing (FCD-09 WP-02)."""

from dataclasses import dataclass
import hashlib
from pathlib import Path


class FileValidationError(Exception):
    """Raised when an uploaded file violates security, size, or format constraints."""


@dataclass(frozen=True)
class ValidatedUpload:
    """Result of successful upload content inspection."""

    filename: str
    content_type: str
    size_bytes: int
    checksum_sha256: str


ALLOWED_EXTENSIONS_MAP: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
}


def sanitize_filename(filename: str) -> str:
    """Normalize and sanitize a user-supplied filename to prevent path traversal."""
    if not filename or not isinstance(filename, str):
        raise FileValidationError("Invalid filename.")
    normalized = Path(filename.replace("\\", "/")).name.strip()
    if not normalized or normalized in {".", ".."} or "/" in normalized or "\\" in normalized:
        raise FileValidationError("Filename contains invalid characters or path traversal.")
    if len(normalized) > 180:
        raise FileValidationError("Filename is too long (maximum 180 characters).")
    return normalized


def detect_mime_type(content: bytes) -> str | None:
    """Sniff MIME type from content header magic bytes."""
    if len(content) < 4:
        return None
    # JPEG magic bytes: FF D8 FF
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    # PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    # WebP: RIFF .... WEBP
    if content.startswith(b"RIFF") and len(content) >= 12 and content[8:12] == b"WEBP":
        return "image/webp"
    # PDF magic bytes: %PDF-
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    return None


def validate_file_content(
    filename: str,
    content: bytes,
    max_bytes: int,
    allowed_mimes: set[str],
) -> ValidatedUpload:
    """Perform rigorous inspection on uploaded file content."""
    clean_filename = sanitize_filename(filename)
    size = len(content)

    if size == 0:
        raise FileValidationError("Uploaded file is empty.")
    if size > max_bytes:
        raise FileValidationError(
            f"File size ({size} bytes) exceeds maximum permitted limit ({max_bytes} bytes)."
        )

    ext = Path(clean_filename).suffix.lower()
    expected_mime = ALLOWED_EXTENSIONS_MAP.get(ext)
    if not expected_mime:
        raise FileValidationError(f"File extension '{ext}' is not supported.")

    detected_mime = detect_mime_type(content)
    if detected_mime is None or detected_mime != expected_mime:
        raise FileValidationError(
            f"Content does not match extension '{ext}' (detected '{detected_mime}')."
        )

    if detected_mime not in allowed_mimes:
        raise FileValidationError(f"MIME type '{detected_mime}' is not permitted by configuration.")

    checksum = hashlib.sha256(content).hexdigest()
    return ValidatedUpload(
        filename=clean_filename,
        content_type=detected_mime,
        size_bytes=size,
        checksum_sha256=checksum,
    )
