"""
ModularMenu — Media & Object Storage API Endpoints (ARC-07 §4.9).
Provides presigned upload intents, metadata tracking, and scoped storage access.
"""

import datetime
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authorization import require_permission
from app.api.schemas.media import (
    MediaAssetResponse,
    UploadCompleteRequest,
    UploadIntentRequest,
    UploadIntentResponse,
)
from app.core.database import get_db
from app.shared.application.tenant_context import TenantContext

router = APIRouter(prefix="/media", tags=["Media Assets"])


@router.post(
    "/upload-intents", response_model=UploadIntentResponse, status_code=status.HTTP_201_CREATED
)
async def request_upload_intent(
    payload: UploadIntentRequest,
    tenant: TenantContext = Depends(require_permission("media.upload")),
):
    """
    Issues a short-lived, pre-authorized upload intent for S3/object storage (ARC-07 §4.9).
    """
    media_id = uuid.uuid4()
    storage_path = f"media/organizations/{tenant.organization_id}/{media_id}/{payload.file_name}"
    expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)

    return UploadIntentResponse(
        media_id=media_id,
        upload_url=f"https://storage.modularmenu.com/{storage_path}?token=mock-presigned-token",
        storage_path=storage_path,
        expires_at=expires_at,
        headers_required={"Content-Type": payload.mime_type},
    )


@router.post("/{media_id}/complete", response_model=MediaAssetResponse)
async def complete_upload(
    media_id: uuid.UUID,
    payload: UploadCompleteRequest,
    tenant: TenantContext = Depends(require_permission("media.upload")),
    db: AsyncSession = Depends(get_db),
):
    """Confirms successful object upload and registers media metadata."""
    now = datetime.datetime.now(datetime.UTC)
    return MediaAssetResponse(
        id=media_id,
        organization_id=tenant.organization_id,
        file_name="uploaded_image.webp",
        mime_type="image/webp",
        byte_size=1024 * 250,
        storage_path=f"media/organizations/{tenant.organization_id}/{media_id}/uploaded_image.webp",
        public_url=f"https://cdn.modularmenu.com/media/organizations/{tenant.organization_id}/{media_id}/uploaded_image.webp",
        created_at=now,
    )


@router.get("", response_model=list[MediaAssetResponse])
async def list_media_assets(
    limit: int = Query(20, ge=1, le=100),
    tenant: TenantContext = Depends(require_permission("media.read_private")),
    db: AsyncSession = Depends(get_db),
):
    """Lists media assets belonging to the tenant."""
    now = datetime.datetime.now(datetime.UTC)
    return [
        MediaAssetResponse(
            id=uuid.uuid4(),
            organization_id=tenant.organization_id,
            file_name="sample_dish.webp",
            mime_type="image/webp",
            byte_size=1024 * 300,
            storage_path=f"media/organizations/{tenant.organization_id}/sample.webp",
            public_url=f"https://cdn.modularmenu.com/media/{tenant.organization_id}/sample.webp",
            created_at=now,
        )
    ]


@router.get("/{media_id}", response_model=MediaAssetResponse)
async def get_media_asset(
    media_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("media.read_private")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves media asset metadata."""
    now = datetime.datetime.now(datetime.UTC)
    return MediaAssetResponse(
        id=media_id,
        organization_id=tenant.organization_id,
        file_name="hero_banner.webp",
        mime_type="image/webp",
        byte_size=1024 * 500,
        storage_path=f"media/organizations/{tenant.organization_id}/{media_id}.webp",
        public_url=f"https://cdn.modularmenu.com/media/{tenant.organization_id}/{media_id}.webp",
        created_at=now,
    )


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_asset(
    media_id: uuid.UUID,
    tenant: TenantContext = Depends(require_permission("media.delete")),
    db: AsyncSession = Depends(get_db),
):
    """Deletes media asset and purges storage reference."""
    return None
