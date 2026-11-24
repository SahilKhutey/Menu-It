"""Idempotency FastAPI dependencies and context (FCD-07 WP-11)."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.api.dependencies.authentication import (
    AuthenticatedPrincipal,
    get_authenticated_principal,
)
from menu_it.api.dependencies.tenant import (
    TenantContext,
    get_tenant_context_from_request,
)
from menu_it.database.session import get_db_session
from menu_it.infrastructure.idempotency.exceptions import (
    IdempotencyConflictError,
    IdempotentReplayException,
)
from menu_it.infrastructure.idempotency.service import IdempotencyService


class IdempotencyContext:
    """Carries idempotency verification state for the current request."""

    def __init__(
        self,
        key: str,
        request_hash: str,
        organization_id: UUID,
        actor_id: UUID | None,
    ) -> None:
        self.key = key
        self.request_hash = request_hash
        self.organization_id = organization_id
        self.actor_id = actor_id
        self.saved = False

    async def save(
        self,
        session: AsyncSession,
        response_status: int,
        response_body: Any,
        ttl_seconds: int = IdempotencyService.DEFAULT_TTL_SECONDS,
    ) -> None:
        """Persist recorded response into database."""
        if self.saved:
            return
        await IdempotencyService.save_record(
            session=session,
            organization_id=self.organization_id,
            actor_id=self.actor_id,
            key=self.key,
            request_hash=self.request_hash,
            response_status=response_status,
            response_body=response_body,
            ttl_seconds=ttl_seconds,
        )
        self.saved = True


async def check_idempotency(
    request: Request,
    tenant: Annotated[TenantContext, Depends(get_tenant_context_from_request)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    principal: Annotated[AuthenticatedPrincipal, Depends(get_authenticated_principal)],
) -> IdempotencyContext | None:
    """Validate Idempotency-Key header against previous requests.

    If key is absent, returns None.
    If key is present and expired, purges and continues as new.
    If key is present and matches previous payload, raises IdempotentReplayException.
    If key is present and payload differs, raises IdempotencyConflictError.
    """
    key = request.headers.get("Idempotency-Key")
    if not key:
        return None

    key = key.strip()
    if not (1 <= len(key) <= 128):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Idempotency-Key header: length must be between 1 and 128 characters.",
        )

    # Read body bytes
    body_bytes = await request.body()
    req_hash = IdempotencyService.compute_payload_hash(
        method=request.method,
        path=request.url.path,
        body=body_bytes,
    )

    actor_id = principal.user_id if principal else None

    # Check for existing record
    record = await IdempotencyService.get_record(
        session=session,
        organization_id=tenant.organization_id,
        actor_id=actor_id,
        key=key,
    )

    if record is not None:
        if record.request_hash != req_hash:
            raise IdempotencyConflictError(
                message=(
                    f"Idempotency conflict: key '{key}' was previously used "
                    "with a different request payload."
                ),
                key=key,
            )
        # Identical payload: replay stored response
        raise IdempotentReplayException(
            status_code=record.response_status,
            response_body=record.response_body,
        )

    context = IdempotencyContext(
        key=key,
        request_hash=req_hash,
        organization_id=tenant.organization_id,
        actor_id=actor_id,
    )
    request.state.idempotency_context = context
    return context
