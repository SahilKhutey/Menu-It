"""Background jobs platform package initialization (FCD-10 WP-03)."""

from menu_it.platform.jobs.contracts import JobContext, JobEnvelope, JobStatus
from menu_it.platform.jobs.dead_letter import DeadLetterService
from menu_it.platform.jobs.registry import (
    JOB_REGISTRY,
    get_job_handler,
    is_valid_job_type,
    register_job_type,
)
from menu_it.platform.jobs.retry import (
    PermanentJobError,
    RetryableJobError,
    calculate_retry_delay,
    is_retryable_error,
)
from menu_it.platform.jobs.service import JobService
from menu_it.platform.jobs.worker import WorkerSettings

__all__ = [
    "DeadLetterService",
    "JOB_REGISTRY",
    "JobContext",
    "JobEnvelope",
    "JobService",
    "JobStatus",
    "PermanentJobError",
    "RetryableJobError",
    "WorkerSettings",
    "calculate_retry_delay",
    "get_job_handler",
    "is_retryable_error",
    "is_valid_job_type",
    "register_job_type",
]
