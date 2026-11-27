"""Job registry for validating permitted job types and handlers (FCD-10 WP-03)."""

from collections.abc import Callable
from typing import Any

# Global registered job types mapping job_type to handler function
JOB_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_job_type(job_type: str, handler: Callable[..., Any]) -> None:
    """Register a permitted job type and its handler function."""
    if not job_type or ":" in job_type:
        raise ValueError("Job type must be non-empty and cannot contain ':'.")
    JOB_REGISTRY[job_type] = handler


def is_valid_job_type(job_type: str) -> bool:
    """Check if job type is permitted to execute."""
    return job_type in JOB_REGISTRY


def get_job_handler(job_type: str) -> Callable[..., Any]:
    """Retrieve handler for job type, raising ValueError if unregistered."""
    if job_type not in JOB_REGISTRY:
        raise ValueError(f"Unregistered job type: '{job_type}'. Execution denied.")
    return JOB_REGISTRY[job_type]
