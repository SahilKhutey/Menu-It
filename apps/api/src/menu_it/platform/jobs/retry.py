"""Exponential backoff, jitter calculation and failure classification (FCD-10 WP-04)."""

import random
from collections.abc import Callable


class PermanentJobError(Exception):
    """Exception indicating non-retryable failure (dead-letter immediately)."""

    pass


class RetryableJobError(Exception):
    """Exception indicating transient failure that should be retried."""

    pass


def calculate_retry_delay(
    attempt: int,
    initial_delay: int = 5,
    maximum_delay: int = 900,
    multiplier: int = 2,
    jitter_fraction: float = 0.1,
    random_fn: Callable[[], float] | None = None,
) -> float:
    """Calculate exponential backoff delay with random jitter.

    Formula:
        d_n = min(d_max, d_0 * multiplier^(attempt - 1)) + Jitter
    """
    if attempt <= 0:
        attempt = 1
    base_delay = min(maximum_delay, initial_delay * (multiplier ** (attempt - 1)))

    if jitter_fraction > 0:
        rnd = random_fn() if random_fn else random.random()
        jitter = rnd * jitter_fraction * base_delay
    else:
        jitter = 0.0

    return min(float(maximum_delay), float(base_delay + jitter))


def is_retryable_error(exc: Exception) -> bool:
    """Classify whether an exception is transient or permanent.

    Non-retryable errors are dead-lettered immediately.
    """
    if isinstance(exc, PermanentJobError):
        return False
    if isinstance(exc, RetryableJobError):
        return True

    # Known non-retryable programming/validation errors
    non_retryable_types = (
        ValueError,
        TypeError,
        KeyError,
        AssertionError,
        NotImplementedError,
    )
    if isinstance(exc, non_retryable_types):
        return False

    # Known transient/network errors
    retryable_types = (
        ConnectionError,
        TimeoutError,
        OSError,
    )
    if isinstance(exc, retryable_types):
        return True

    # Check error message for transient keywords
    msg = str(exc).lower()
    return any(term in msg for term in ("connection refused", "timeout", "rate limit"))
