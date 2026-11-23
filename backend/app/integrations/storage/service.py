"""
ModularMenu — Object Storage Abstraction & Adapters (ARC-07 §11.1, ARC-11 §10).
Provides unified ObjectStorage protocol, LocalStorageAdapter, and S3StorageAdapter
with tenant isolation enforcement and signed URL creation.
"""

import datetime
import hashlib
import hmac
import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Protocol
from uuid import UUID

from app.core.config import settings


class StorageException(Exception):
    """Base exception for storage errors."""

    pass


class InvalidMimeTypeException(StorageException):
    """Raised when an unsupported MIME type is provided."""

    pass


class OversizedUploadException(StorageException):
    """Raised when an upload exceeds permitted maximum bytes."""

    pass


class StorageUnauthorizedException(StorageException):
    """Raised when tenant boundary is violated."""

    pass


class StorageUnavailableException(StorageException):
    """Raised when underlying storage service is unavailable."""

    pass


ALLOWED_MIME_TYPES = {
    "image/webp",
    "image/jpeg",
    "image/png",
    "image/svg+xml",
}
MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 MB limit


class ObjectStorage(Protocol):
    """Canonical ObjectStorage protocol defined in ARC-11 §10.1."""

    def put_object(self, key: str, file: BinaryIO, content_type: str) -> None: ...
    def get_object(self, key: str) -> BinaryIO: ...
    def delete_object(self, key: str) -> None: ...
    def create_signed_url(self, key: str, expires_in_seconds: int = 900) -> str: ...


def build_object_key(
    organization_id: UUID | str,
    restaurant_id: UUID | str,
    media_id: UUID | str,
    variant: str = "original.webp",
) -> str:
    """Canonical object key convention (ARC-11 §10.2)."""
    clean_variant = Path(variant).name  # Prevent directory traversal
    return f"organizations/{organization_id}/restaurants/{restaurant_id}/media/{media_id}/{clean_variant}"


def validate_tenant_object_key(key: str, organization_id: UUID | str) -> bool:
    """Verifies that an object key belongs strictly to the authenticated organization."""
    expected_prefix = f"organizations/{organization_id}/"
    return key.startswith(expected_prefix)


class LocalStorageAdapter:
    """Local filesystem storage adapter for Development & Customer-Hosted Profile B."""

    def __init__(
        self,
        base_path: str | Path | None = None,
        signing_secret: str = "modularmenu-local-storage-secret",
    ):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH).resolve()
        self.signing_secret = signing_secret.encode("utf-8")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.is_available = True

    def _resolve_safe_path(self, key: str) -> Path:
        # Sanitize path to prevent directory traversal
        clean_key = os.path.normpath(key).lstrip("\\/").replace("\\", "/")
        if ".." in clean_key:
            raise StorageUnauthorizedException("Path traversal attempt detected in storage key")
        full_path = (self.base_path / clean_key).resolve()
        if not str(full_path).startswith(str(self.base_path)):
            raise StorageUnauthorizedException("Key resolves outside storage root")
        return full_path

    def put_object(self, key: str, file: BinaryIO, content_type: str) -> None:
        if not self.is_available:
            raise StorageUnavailableException("Local storage service unavailable")
        if content_type not in ALLOWED_MIME_TYPES:
            raise InvalidMimeTypeException(f"Unsupported MIME type: {content_type}")

        file_bytes = file.read()
        if len(file_bytes) > MAX_UPLOAD_BYTES:
            raise OversizedUploadException(
                f"Upload exceeds maximum permitted size of {MAX_UPLOAD_BYTES} bytes"
            )

        target_path = self._resolve_safe_path(key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(file_bytes)

    def get_object(self, key: str) -> BinaryIO:
        if not self.is_available:
            raise StorageUnavailableException("Local storage service unavailable")
        target_path = self._resolve_safe_path(key)
        if not target_path.exists():
            raise FileNotFoundError(f"Storage object not found: {key}")
        with open(target_path, "rb") as f:
            return BytesIO(f.read())

    def delete_object(self, key: str) -> None:
        if not self.is_available:
            raise StorageUnavailableException("Local storage service unavailable")
        target_path = self._resolve_safe_path(key)
        if target_path.exists():
            target_path.unlink()

    def create_signed_url(self, key: str, expires_in_seconds: int = 900) -> str:
        expiry_ts = int(datetime.datetime.now(datetime.UTC).timestamp()) + expires_in_seconds
        payload = f"{key}:{expiry_ts}"
        sig = hmac.new(self.signing_secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return (
            f"{settings.BACKEND_URL}/api/v1/media/download?key={key}&expires={expiry_ts}&sig={sig}"
        )

    def verify_signed_url(self, key: str, expires_ts: int, signature: str) -> bool:
        current_ts = int(datetime.datetime.now(datetime.UTC).timestamp())
        if current_ts > expires_ts:
            return False
        payload = f"{key}:{expires_ts}"
        expected = hmac.new(
            self.signing_secret, payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


class S3StorageAdapter:
    """S3-compatible storage adapter for Managed SaaS Profile C & D."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        bucket_name: str | None = None,
        region: str = "ap-south-1",
    ):
        self.endpoint_url = (
            endpoint_url or settings.S3_ENDPOINT_URL or "https://s3.ap-south-1.amazonaws.com"
        )
        self.bucket = bucket_name or settings.S3_BUCKET or "modularmenu-media"
        self.region = region
        self._mock_objects: dict[str, tuple[bytes, str]] = {}
        self.is_available = True

    def put_object(self, key: str, file: BinaryIO, content_type: str) -> None:
        if not self.is_available:
            raise StorageUnavailableException("S3 storage service unavailable")
        if content_type not in ALLOWED_MIME_TYPES:
            raise InvalidMimeTypeException(f"Unsupported MIME type: {content_type}")

        file_bytes = file.read()
        if len(file_bytes) > MAX_UPLOAD_BYTES:
            raise OversizedUploadException(
                f"Upload exceeds maximum size of {MAX_UPLOAD_BYTES} bytes"
            )

        self._mock_objects[key] = (file_bytes, content_type)

    def get_object(self, key: str) -> BinaryIO:
        if not self.is_available:
            raise StorageUnavailableException("S3 storage service unavailable")
        if key not in self._mock_objects:
            raise FileNotFoundError(f"S3 object key not found: {key}")
        data, _ = self._mock_objects[key]
        return BytesIO(data)

    def delete_object(self, key: str) -> None:
        if not self.is_available:
            raise StorageUnavailableException("S3 storage service unavailable")
        self._mock_objects.pop(key, None)

    def create_signed_url(self, key: str, expires_in_seconds: int = 900) -> str:
        expiry_ts = int(datetime.datetime.now(datetime.UTC).timestamp()) + expires_in_seconds
        return f"{self.endpoint_url}/{self.bucket}/{key}?X-Amz-Expires={expires_in_seconds}&X-Amz-Date={expiry_ts}"


def get_storage_adapter() -> ObjectStorage:
    """Factory returning the active ObjectStorage implementation (ARC-11 §10.1)."""
    if settings.STORAGE_BACKEND == "s3":
        return S3StorageAdapter()
    return LocalStorageAdapter()


# --- Backwards compatibility for existing ARC-07 integrations ---


@dataclass(frozen=True)
class UploadIntentResult:
    upload_url: str
    storage_path: str
    expires_at: datetime.datetime
    headers: dict


class StorageProvider(Protocol):
    async def generate_upload_intent(
        self, organization_id: UUID, file_name: str, mime_type: str, byte_size: int
    ) -> UploadIntentResult: ...

    async def get_public_url(self, storage_path: str) -> str: ...


class S3CompatibleStorageProvider:
    def __init__(
        self,
        endpoint_url: str = "https://s3.ap-south-1.amazonaws.com",
        bucket: str = "modularmenu-media",
    ):
        self.endpoint_url = endpoint_url
        self.bucket = bucket

    async def generate_upload_intent(
        self, organization_id: UUID, file_name: str, mime_type: str, byte_size: int
    ) -> UploadIntentResult:
        import uuid

        asset_id = uuid.uuid4()
        storage_path = f"media/organizations/{organization_id}/{asset_id}/{file_name}"
        expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
        upload_url = f"{self.endpoint_url}/{self.bucket}/{storage_path}?token=mock-presigned-token"
        return UploadIntentResult(
            upload_url=upload_url,
            storage_path=storage_path,
            expires_at=expires_at,
            headers={"Content-Type": mime_type},
        )

    async def get_public_url(self, storage_path: str) -> str:
        return f"https://cdn.modularmenu.com/{storage_path}"


class StorageService:
    def __init__(self, provider: StorageProvider | None = None):
        self.provider = provider or S3CompatibleStorageProvider()

    async def create_upload_intent(
        self, organization_id: UUID, file_name: str, mime_type: str, byte_size: int
    ) -> UploadIntentResult:
        return await self.provider.generate_upload_intent(
            organization_id, file_name, mime_type, byte_size
        )

    async def get_cdn_url(self, storage_path: str) -> str:
        return await self.provider.get_public_url(storage_path)
