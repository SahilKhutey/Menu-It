"""
ModularMenu — Operation Timeout Policy (ARC-12 §25.1, ADR-0252).
Enforces explicit bounded execution deadlines on all asynchronous operations.
"""

import asyncio
from typing import TypeVar

T = TypeVar("T")

# Standardized operation deadlines (ARC-12 §25.1)
DATABASE_CONNECT_TIMEOUT_SECONDS: float = 5.0
DATABASE_STATEMENT_TIMEOUT_SECONDS: float = 30.0
EXTERNAL_HTTP_CONNECT_SECONDS: float = 2.0
EXTERNAL_HTTP_READ_SECONDS: float = 5.0
OBJECT_STORAGE_TIMEOUT_SECONDS: float = 15.0
WORKER_JOB_TIMEOUT_SECONDS: float = 60.0
GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS: float = 15.0


async def run_with_timeout(coroutine, timeout_seconds: float) -> T:
    """Execute coroutine with strict deadline; raises TimeoutError on expiration."""
    return await asyncio.wait_for(coroutine, timeout=timeout_seconds)
