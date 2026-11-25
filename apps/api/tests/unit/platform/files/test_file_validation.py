"""Unit tests for file upload validation and magic-byte sniffing (FCD-09 WP-02)."""

import pytest

from menu_it.platform.files.application.validation import (
    FileValidationError,
    sanitize_filename,
    validate_file_content,
)

JPEG_MAGIC = b"\xff\xd8\xff\xe0" + b"\x00" * 20
PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
WEBP_MAGIC = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"\x00" * 20
PDF_MAGIC = b"%PDF-1.4\n" + b"\x00" * 20
ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


def test_sanitize_filename_prevents_traversal():
    """Strips path traversal sequences and enforces character and length bounds."""
    assert sanitize_filename("avatar.png") == "avatar.png"
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\secret.key") == "secret.key"

    with pytest.raises(FileValidationError, match="Invalid filename"):
        sanitize_filename("")

    with pytest.raises(FileValidationError, match="Filename is too long"):
        sanitize_filename("a" * 181 + ".png")


def test_validate_valid_files():
    """Validates legitimate JPEG, PNG, WebP, and PDF content."""
    res_jpeg = validate_file_content("test.jpg", JPEG_MAGIC, 100000, ALLOWED_MIMES)
    assert res_jpeg.content_type == "image/jpeg"
    assert res_jpeg.size_bytes == len(JPEG_MAGIC)

    res_png = validate_file_content("test.png", PNG_MAGIC, 100000, ALLOWED_MIMES)
    assert res_png.content_type == "image/png"

    res_webp = validate_file_content("test.webp", WEBP_MAGIC, 100000, ALLOWED_MIMES)
    assert res_webp.content_type == "image/webp"

    res_pdf = validate_file_content("doc.pdf", PDF_MAGIC, 100000, ALLOWED_MIMES)
    assert res_pdf.content_type == "application/pdf"


def test_validate_rejects_empty_file():
    """Empty files are rejected."""
    with pytest.raises(FileValidationError, match="Uploaded file is empty"):
        validate_file_content("empty.png", b"", 100000, ALLOWED_MIMES)


def test_validate_rejects_exceeded_size():
    """Files exceeding size limit are rejected."""
    with pytest.raises(FileValidationError, match="exceeds maximum permitted limit"):
        validate_file_content("test.png", PNG_MAGIC, 10, ALLOWED_MIMES)


def test_validate_rejects_mismatched_content_and_extension():
    """Discrepancy between magic bytes and extension fails validation."""
    with pytest.raises(FileValidationError, match="Content does not match extension"):
        validate_file_content("fake_image.png", JPEG_MAGIC, 100000, ALLOWED_MIMES)

    with pytest.raises(FileValidationError, match="Content does not match extension"):
        validate_file_content("wrong_pdf.pdf", PNG_MAGIC, 100000, ALLOWED_MIMES)

    with pytest.raises(FileValidationError, match="is not supported"):
        validate_file_content("script.sh", b"#!/bin/bash\n", 100000, ALLOWED_MIMES)


def test_validate_rejects_unsupported_mime():
    """Content types not in allowed set are rejected."""
    with pytest.raises(FileValidationError, match="not permitted by configuration"):
        validate_file_content("doc.pdf", PDF_MAGIC, 100000, {"image/jpeg", "image/png"})
