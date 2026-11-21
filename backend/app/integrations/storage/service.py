"""
ModularMenu — Object Storage Integration Contracts & Adapters (ARC-07 §11.1, ARC07-D23).
"""
import datetime
from dataclasses import dataclass
from typing import Optional, Protocol
from uuid import UUID


@dataclass(frozen=True)
class UploadIntentResult:
    upload_url: str
    storage_path: str
    expires_at: datetime.datetime
    headers: dict


class StorageProvider(Protocol):
    async def generate_upload_intent(
        self, organization_id: UUID, file_name: str, mime_type: str, byte_size: int
    ) -> UploadIntentResult:
        ...

    async def get_public_url(self, storage_path: str) -> str:
        ...


class S3CompatibleStorageProvider:
    def __init__(self, endpoint_url: str = "https://s3.ap-south-1.amazonaws.com", bucket: str = "modularmenu-media"):
        self.endpoint_url = endpoint_url
        self.bucket = bucket

    async def generate_upload_intent(
        self, organization_id: UUID, file_name: str, mime_type: str, byte_size: int
    ) -> UploadIntentResult:
        import uuid
        asset_id = uuid.uuid4()
        storage_path = f"media/organizations/{organization_id}/{asset_id}/{file_name}"
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
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
    def __init__(self, provider: Optional[StorageProvider] = None):
        self.provider = provider or S3CompatibleStorageProvider()

    async def create_upload_intent(
        self, organization_id: UUID, file_name: str, mime_type: str, byte_size: int
    ) -> UploadIntentResult:
        return await self.provider.generate_upload_intent(organization_id, file_name, mime_type, byte_size)

    async def get_cdn_url(self, storage_path: str) -> str:
        return await self.provider.get_public_url(storage_path)
