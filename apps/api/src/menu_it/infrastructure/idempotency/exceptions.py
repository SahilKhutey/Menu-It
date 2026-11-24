"""Idempotency exceptions (FCD-07 WP-11)."""

from typing import Any


class IdempotencyError(Exception):
    """Base exception for idempotency violations."""


class IdempotencyConflictError(IdempotencyError):
    """Raised when an idempotency key is reused with a different request payload."""

    def __init__(
        self,
        message: str = (
            "Idempotency conflict: key was previously used with a different request payload."
        ),
        key: str = "",
    ) -> None:
        self.message = message
        self.key = key
        super().__init__(self.message)


class IdempotentReplayException(IdempotencyError):
    """Raised by idempotency dependency to short-circuit execution with stored response."""

    def __init__(self, status_code: int, response_body: Any) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__("Idempotent replay")
