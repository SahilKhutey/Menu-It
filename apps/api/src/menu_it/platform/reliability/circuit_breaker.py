"""Circuit breaker state machine for third-party and remote calls (FCD-11 WP-11)."""

import asyncio
import logging
import time
from collections.abc import Callable
from enum import StrEnum
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(StrEnum):
    """Lifecycle states of a circuit breaker."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted on an open circuit breaker."""

    def __init__(self, name: str, retry_after: float) -> None:
        self.name = name
        self.retry_after = retry_after
        msg = (
            f"Circuit breaker '{name}' is OPEN. Remote dependency is degraded. "
            f"Retry after {retry_after:.1f}s."
        )
        super().__init__(msg)


class CircuitBreaker:
    """State machine protecting application from cascading failures during dependency outages."""

    def __init__(
        self,
        name: str,
        *,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_state_change = time.time()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        return self._state

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a callable protected by this circuit breaker."""
        async with self._lock:
            now = time.time()

            if self._state == CircuitState.OPEN:
                if now - self._last_state_change >= self.recovery_timeout:
                    logger.info("Circuit breaker '%s' transition: OPEN -> HALF_OPEN", self.name)
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    self._last_state_change = now
                else:
                    retry_after = max(0.1, self.recovery_timeout - (now - self._last_state_change))
                    raise CircuitBreakerOpenException(self.name, retry_after)

        # Execute target callable outside lock so long operations don't block state queries
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
        except Exception as exc:
            await self._record_failure()
            raise exc

        await self._record_success()
        return result

    async def _record_failure(self) -> None:
        async with self._lock:
            now = time.time()
            if self._state == CircuitState.HALF_OPEN:
                logger.warning(
                    "Circuit breaker '%s' failed in HALF_OPEN probe; returning to OPEN",
                    self.name,
                )
                self._state = CircuitState.OPEN
                self._last_state_change = now
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    logger.error(
                        "Circuit breaker '%s' tripped: CLOSED -> OPEN (failures: %d)",
                        self.name,
                        self._failure_count,
                    )
                    self._state = CircuitState.OPEN
                    self._last_state_change = now

    async def _record_success(self) -> None:
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    logger.info(
                        "Circuit breaker '%s' recovered: HALF_OPEN -> CLOSED",
                        self.name,
                    )
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self._last_state_change = time.time()
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    async def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state."""
        async with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_state_change = time.time()
