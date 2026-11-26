"""Internal background job and dead-letter queue management APIs (FCD-10 WP-09)."""

from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.api.dependencies.authentication import get_authenticated_principal
from menu_it.api.dependencies.tenant import get_optional_organization_id
from menu_it.api.schemas.common import APIResponse, ResponseMeta
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.database.session import get_db_session
from menu_it.platform.jobs.contracts import JobContext
from menu_it.platform.jobs.dead_letter import DeadLetterService
from menu_it.platform.jobs.service import JobService

router = APIRouter(
    prefix="/internal",
    tags=["Internal Jobs & DLQ"],
)


class SubmitJobRequest(BaseModel):
    """Payload for submitting a background job."""

    model_config = ConfigDict(extra="forbid")

    job_type: str
    payload: dict[str, Any]
    idempotency_key: str | None = None


class JobResponseData(BaseModel):
    """Transport schema for background job metadata."""

    model_config = ConfigDict(extra="forbid")

    job_id: UUID
    job_type: str
    status: str
    created_at: datetime


class DeadLetterResponseData(BaseModel):
    """Transport schema for dead-letter records."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    job_id: UUID
    job_type: str
    failure_code: str
    failure_message: str
    attempts: int
    dead_lettered_at: datetime
    correlation_id: str
    replayed_at: datetime | None = None


@router.post(
    "/jobs",
    response_model=APIResponse[JobResponseData],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit Background Job",
)
async def submit_job_endpoint(
    req: SubmitJobRequest,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[JobResponseData]:
    """Submit a permitted background job for execution."""
    service = JobService(session)
    corr_id = x_request_id or "internal-submit"
    context = JobContext(
        organization_id=organization_id,
        actor_user_id=principal.user_id,
        correlation_id=corr_id,
        initiated_by="user",
    )
    try:
        envelope = await service.submit_job(
            job_type=req.job_type,
            payload=req.payload,
            context=context,
            idempotency_key=req.idempotency_key,
        )
        await session.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        data=JobResponseData(
            job_id=envelope.job_id,
            job_type=envelope.job_type,
            status="queued",
            created_at=envelope.created_at,
        ),
        error=None,
        meta=ResponseMeta(
            request_id=corr_id,
            timestamp=datetime.now(UTC),
        ),
    )


@router.get(
    "/jobs/{job_id}",
    response_model=APIResponse[JobResponseData],
    summary="Get Job Status",
)
async def get_job_endpoint(
    job_id: UUID,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[JobResponseData]:
    """Retrieve execution status of a submitted job."""
    service = JobService(session)
    job = await service.get_job(job_id=job_id, organization_id=organization_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return APIResponse(
        success=True,
        data=JobResponseData(
            job_id=job.id,
            job_type=job.job_type,
            status=job.status,
            created_at=job.created_at,
        ),
        error=None,
        meta=ResponseMeta(
            request_id=x_request_id or "internal-get",
            timestamp=datetime.now(UTC),
        ),
    )


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=APIResponse[dict[str, str]],
    summary="Cancel Background Job",
)
async def cancel_job_endpoint(
    job_id: UUID,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Request cancellation of a queued job."""
    service = JobService(session)
    cancelled = await service.cancel_job(job_id=job_id, organization_id=organization_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be cancelled (either not found, or already running/completed).",
        )
    await session.commit()
    return APIResponse(
        success=True,
        data={"status": "cancelled", "job_id": str(job_id)},
        error=None,
        meta=ResponseMeta(
            request_id=x_request_id or "internal-cancel",
            timestamp=datetime.now(UTC),
        ),
    )


@router.get(
    "/dead-letters",
    response_model=APIResponse[list[DeadLetterResponseData]],
    summary="List Dead-Letter Jobs",
)
async def list_dead_letters_endpoint(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[list[DeadLetterResponseData]]:
    """List dead letters with tenant boundary scoping."""
    service = DeadLetterService(session)
    records = await service.list_dead_letters(
        organization_id=organization_id,
        limit=limit,
        offset=offset,
    )
    data = [
        DeadLetterResponseData(
            id=r.id,
            job_id=r.job_id,
            job_type=r.job_type,
            failure_code=r.failure_code,
            failure_message=r.failure_message,
            attempts=r.attempts,
            dead_lettered_at=r.dead_lettered_at,
            correlation_id=r.correlation_id,
            replayed_at=r.replayed_at,
        )
        for r in records
    ]
    return APIResponse(
        success=True,
        data=data,
        error=None,
        meta=ResponseMeta(
            request_id=x_request_id or "internal-dlq-list",
            timestamp=datetime.now(UTC),
        ),
    )


@router.get(
    "/dead-letters/{record_id}",
    response_model=APIResponse[DeadLetterResponseData],
    summary="Get Dead-Letter Job",
)
async def get_dead_letter_endpoint(
    record_id: UUID,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[DeadLetterResponseData]:
    """Retrieve details of a dead letter record."""
    service = DeadLetterService(session)
    record = await service.get_dead_letter(record_id, organization_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dead-letter record not found."
        )

    return APIResponse(
        success=True,
        data=DeadLetterResponseData(
            id=record.id,
            job_id=record.job_id,
            job_type=record.job_type,
            failure_code=record.failure_code,
            failure_message=record.failure_message,
            attempts=record.attempts,
            dead_lettered_at=record.dead_lettered_at,
            correlation_id=record.correlation_id,
            replayed_at=record.replayed_at,
        ),
        error=None,
        meta=ResponseMeta(
            request_id=x_request_id or "internal-dlq-get",
            timestamp=datetime.now(UTC),
        ),
    )


@router.post(
    "/dead-letters/{record_id}/replay",
    response_model=APIResponse[JobResponseData],
    summary="Replay Dead-Letter Job",
)
async def replay_dead_letter_endpoint(
    record_id: UUID,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    organization_id: Annotated[UUID | None, Depends(get_optional_organization_id)] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[JobResponseData]:
    """Authorized replay of an exhausted or failed job."""
    dl_service = DeadLetterService(session)
    record = await dl_service.get_dead_letter(record_id, organization_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dead-letter record not found."
        )

    job_service = JobService(session)
    context = JobContext(
        organization_id=record.organization_id,
        actor_user_id=principal.user_id,
        correlation_id=f"replay-{record.id}",
        initiated_by="user",
    )
    envelope = await job_service.submit_job(
        job_type=record.job_type,
        payload=record.payload,
        context=context,
    )
    await dl_service.mark_replayed(
        record_id=record.id,
        replayed_by=principal.user_id,
        organization_id=organization_id,
    )
    await session.commit()

    return APIResponse(
        success=True,
        data=JobResponseData(
            job_id=envelope.job_id,
            job_type=envelope.job_type,
            status="queued",
            created_at=envelope.created_at,
        ),
        error=None,
        meta=ResponseMeta(
            request_id=x_request_id or "internal-dlq-replay",
            timestamp=datetime.now(UTC),
        ),
    )
