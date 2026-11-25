"""Domain contracts and data structures for background jobs (FCD-10 WP-03)."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class JobStatus(str, Enum):
    """Lifecycle states of a background job."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    RETRY_SCHEDULED = "retry_scheduled"
    DEAD_LETTERED = "dead_lettered"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class JobContext:
    """Explicit context propagated into worker processes (FCD-10 WP-06)."""

    organization_id: UUID | None
    actor_user_id: UUID | None
    correlation_id: str
    initiated_by: str  # "user" | "system" | "scheduler"


@dataclass(frozen=True, slots=True)
class JobEnvelope:
    """Standardized serialization envelope for asynchronous jobs."""

    job_id: UUID
    job_type: str
    schema_version: int
    payload: dict[str, Any]
    context: JobContext
    created_at: datetime
    idempotency_key: str
