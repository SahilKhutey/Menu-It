"""
ModularMenu — Tenant Job Context & Asynchronous Worker Isolation (ARC-05 §13, ARC05-D16).
Provides secure execution envelopes for asynchronous and background tasks,
guaranteeing transaction-scoped tenant isolation and prevention of context leakage.
"""
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar
from uuid import UUID

from app.shared.domain.tenant_exceptions import (
    CrossTenantAccessException,
    InvalidTenantContextException,
)

T = TypeVar("T")


@dataclass(frozen=True)
class TenantJobContext:
    """Authoritative execution envelope for tenant-scoped asynchronous jobs."""
    organization_id: UUID
    restaurant_id: Optional[UUID]
    initiating_user_id: Optional[UUID]
    correlation_id: str
    job_id: str
    purpose: str

    def __post_init__(self) -> None:
        if not self.organization_id:
            raise InvalidTenantContextException("Worker job envelope requires a valid organization_id")
        if not self.job_id:
            raise InvalidTenantContextException("Worker job envelope requires a job_id")
        if not self.purpose:
            raise InvalidTenantContextException("Worker job envelope requires an explicit purpose")


class TenantWorkerRunner:
    """
    Executes worker tasks with strict tenant context setup and teardown,
    preventing state leakage between consecutive jobs on worker processes.
    """
    def __init__(self) -> None:
        self._active_tenant: Optional[UUID] = None

    @property
    def active_tenant(self) -> Optional[UUID]:
        return self._active_tenant

    def run_job(
        self,
        job_ctx: TenantJobContext,
        target_resource_org_id: UUID,
        task_callable: Callable[[TenantJobContext], T],
    ) -> T:
        """
        Executes a background task after verifying resource ownership against the job envelope.
        Cleans up context unconditionally on completion or failure.
        """
        # Step 1: Validate resource ownership against job envelope
        if target_resource_org_id != job_ctx.organization_id:
            raise CrossTenantAccessException(
                f"Worker job '{job_ctx.job_id}' forged target resource: envelope org "
                f"'{job_ctx.organization_id}' != resource org '{target_resource_org_id}'"
            )

        try:
            # Step 2: Establish worker execution tenant
            self._active_tenant = job_ctx.organization_id
            # Step 3: Run the task
            result = task_callable(job_ctx)
            return result
        finally:
            # Step 4: Clear context unconditionally to prevent worker pooling leakage
            self._active_tenant = None
