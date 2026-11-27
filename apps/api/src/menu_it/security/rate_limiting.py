"""Rate limiting interfaces and in-memory adapter (FCD-05 §17.1)."""

import threading
from collections import defaultdict
from datetime import UTC, datetime, timedelta


class RateLimitExceededError(Exception):
    """Raised when request rate threshold is exceeded."""


class InMemoryRateLimiter:
    """Thread-safe in-memory sliding window rate limiter for development and testing."""

    def __init__(self):
        self._history: dict[str, list[datetime]] = defaultdict(list)
        self._lock = threading.Lock()

    def check_rate_limit(
        self,
        key: str,
        *,
        max_attempts: int,
        window_seconds: int,
    ) -> bool:
        """Check if request exceeds rate limit.

        Returns True if allowed, False if limit exceeded.
        """
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=window_seconds)

        with self._lock:
            # Prune timestamps outside window
            self._history[key] = [ts for ts in self._history[key] if ts > cutoff]
            if len(self._history[key]) >= max_attempts:
                return False
            self._history[key].append(now)
            return True

    def reset(self, key: str) -> None:
        """Reset history for a key."""
        with self._lock:
            self._history.pop(key, None)

    def clear(self) -> None:
        """Clear all rate limit history."""
        with self._lock:
            self._history.clear()


# Global rate limiter instance
default_rate_limiter = InMemoryRateLimiter()
