"""
ModularMenu — Circuit Breaker Architecture (ARC-12 §24.3, ADR-0253).
Protects core flows by isolating failing external or supporting dependencies.
"""

import time
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenException(Exception):
    """Raised when request is rejected by an open circuit breaker."""

    pass


class CircuitBreaker:
    """State machine governing execution of unstable or failing dependencies."""

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        reset_timeout_seconds: float = 30.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout_seconds = reset_timeout_seconds
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.opened_at: float | None = None

    def allow_request(self, now: float | None = None) -> bool:
        """Evaluate if an outbound request should proceed or be rejected immediately."""
        current_time = now if now is not None else time.monotonic()

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.opened_at is None:
                return False
            if current_time >= (self.opened_at + self.reset_timeout_seconds):
                # Transition to probe state
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        # In HALF_OPEN state, allow probe request
        return True

    def record_success(self) -> None:
        """Reset failure counter and transition back to healthy CLOSED state."""
        self.failures = 0
        self.opened_at = None
        self.state = CircuitState.CLOSED

    def record_failure(self, now: float | None = None) -> None:
        """Increment failure counter and trip circuit breaker if threshold breached."""
        current_time = now if now is not None else time.monotonic()
        self.failures += 1

        if self.failures >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.opened_at = current_time
