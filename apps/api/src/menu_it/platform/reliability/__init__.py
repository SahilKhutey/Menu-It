"""Platform reliability, fault-tolerance, and graceful degradation (FCD-11 WP-11)."""

from menu_it.platform.reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException,
    CircuitState,
)
from menu_it.platform.reliability.timeouts import (
    BACKGROUND_JOB_TIMEOUT,
    DATABASE_QUERY_TIMEOUT,
    DATABASE_TRANSACTION_TIMEOUT,
    HTTP_CLIENT_TIMEOUT,
    NOTIFICATION_DISPATCH_TIMEOUT,
    REDIS_COMMAND_TIMEOUT,
    PlatformTimeouts,
)

__all__ = [
    "BACKGROUND_JOB_TIMEOUT",
    "CircuitBreaker",
    "CircuitBreakerOpenException",
    "CircuitState",
    "DATABASE_QUERY_TIMEOUT",
    "DATABASE_TRANSACTION_TIMEOUT",
    "HTTP_CLIENT_TIMEOUT",
    "NOTIFICATION_DISPATCH_TIMEOUT",
    "PlatformTimeouts",
    "REDIS_COMMAND_TIMEOUT",
]
