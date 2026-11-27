"""File upload, metadata, retrieval, and deletion API endpoints (FCD-09 WP-02)."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, ConfigDict

from menu_it.api.dependencies.authentication import get_authenticated_principal
from menu_it.api.dependencies.tenant import get_optional_organization_id
from menu_it.api.schemas.common import APIResponse, ResponseMeta
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.platform.files.application.service import (
    FileAccessDeniedError,
    FileNotFoundException,
    FileService,
)
from menu_it.platform.files.application.validation import FileValidationError
from menu_it.platform.files.dependencies import get_file_service
from menu_it.platform.files.domain.models import FileVisibility

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


class FileResponseData(BaseModel):
    """File metadata transport representation (excluding internal storage paths)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    visibility: str
    status: str
    created_at: datetime


@router.post(
    "",
    response_model=APIResponse[FileResponseData],
    status_code=status.HTTP_201_CREATED,
    summary="Upload File",
)
async def upload_file(
    file: Annotated[UploadFile, File(description="File binary to upload")],
    service: Annotated[FileService, Depends(get_file_service)],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    visibility: Annotated[FileVisibility, Form()] = FileVisibility.TENANT_PRIVATE,
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[FileResponseData]:
    """Upload a file securely with MIME verification, size checks, and tenant isolation."""
    content = await file.read()
    original_filename = file.filename or "uploaded-file"

    try:
        metadata = await service.upload(
            content=content,
            original_filename=original_filename,
            organization_id=organization_id,
            uploaded_by=principal.user_id,
            visibility=visibility,
            correlation_id=x_request_id,
        )
    except FileValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        data=FileResponseData(
            id=metadata.id,
            filename=metadata.original_filename,
            mime_type=metadata.mime_type,
            size_bytes=metadata.size_bytes,
            visibility=str(metadata.visibility),
            status=str(metadata.status),
            created_at=metadata.created_at,
        ),
        meta=ResponseMeta(request_id=x_request_id or str(metadata.id)),
    )


@router.get(
    "/{file_id}",
    response_model=APIResponse[FileResponseData],
    summary="Get File Metadata",
)
async def get_file_metadata(
    file_id: UUID,
    service: Annotated[FileService, Depends(get_file_service)],
    principal: Annotated[
        AuthenticatedPrincipal | None, Depends(get_authenticated_principal)
    ] = None,
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[FileResponseData]:
    """Retrieve authorized file metadata."""
    user_id = principal.user_id if principal else None
    try:
        metadata = await service.get_metadata(
            file_id=file_id,
            current_org_id=organization_id,
            current_user_id=user_id,
        )
    except FileNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FileAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return APIResponse(
        success=True,
        data=FileResponseData(
            id=metadata.id,
            filename=metadata.original_filename,
            mime_type=metadata.mime_type,
            size_bytes=metadata.size_bytes,
            visibility=str(metadata.visibility),
            status=str(metadata.status),
            created_at=metadata.created_at,
        ),
        meta=ResponseMeta(request_id=x_request_id or str(file_id)),
    )


@router.get(
    "/{file_id}/content",
    summary="Download File Content",
)
async def get_file_content(
    file_id: UUID,
    service: Annotated[FileService, Depends(get_file_service)],
    principal: Annotated[
        AuthenticatedPrincipal | None, Depends(get_authenticated_principal)
    ] = None,
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
) -> Response:
    """Stream authorized file binary content."""
    user_id = principal.user_id if principal else None
    try:
        metadata, stream = await service.get_content(
            file_id=file_id,
            current_org_id=organization_id,
            current_user_id=user_id,
        )
    except FileNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FileAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    raw_bytes = stream.read()
    return Response(
        content=raw_bytes,
        media_type=metadata.mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{metadata.original_filename}"',
            "Content-Length": str(len(raw_bytes)),
        },
    )


@router.delete(
    "/{file_id}",
    response_model=APIResponse[dict[str, str]],
    summary="Delete File",
)
async def delete_file(
    file_id: UUID,
    service: Annotated[FileService, Depends(get_file_service)],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Mark a file as deleted with authorization verification."""
    try:
        await service.delete_file(
            file_id=file_id,
            current_org_id=organization_id,
            current_user_id=principal.user_id,
            correlation_id=x_request_id,
        )
    except FileNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FileAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return APIResponse(
        success=True,
        data={"id": str(file_id), "status": "deleted"},
        meta=ResponseMeta(request_id=x_request_id or str(file_id)),
    )
