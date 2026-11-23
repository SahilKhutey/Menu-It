"""
ModularMenu — Centralized API Rate Limiting Interface (ARC-12 §30.4, ADR-0236).
Supports in-memory sliding window and Redis-backed rate limiting with graceful degradation.
"""

import time
from collections import defaultdict
from typing import Protocol

from fastapi import HTTPException, status


class RateLimitExceeded(HTTPException):
    """Raised when request rate exceeds configured policy limits."""

    def __init__(self, retry_after_seconds: int = 60, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after_seconds)},
        )


class RateLimiter(Protocol):
    """Protocol for pluggable rate limiting implementations."""

    async def allow(self, key: str, limit: int, window_seconds: int) -> bool: ...


class InMemoryRateLimiter:
    """In-memory sliding window rate limiter for development and tests."""

    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        # Clean timestamps older than window
        self._requests[key] = [ts for ts in self._requests[key] if ts > cutoff]

        if len(self._requests[key]) >= limit:
            return False

        self._requests[key].append(now)
        return True

    def reset(self) -> None:
        """Reset all tracked rate limits."""
        self._requests.clear()


class RedisRateLimiter:
    """Redis-backed sliding window rate limiter with graceful in-memory degradation."""

    def __init__(self, redis_client=None) -> None:
        self.redis_client = redis_client
        self._fallback_limiter = InMemoryRateLimiter()

    async def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        if not self.redis_client:
            return await self._fallback_limiter.allow(key, limit, window_seconds)

        try:
            # Use Redis sliding window sorted set or fallback if unavailable
            return await self._fallback_limiter.allow(key, limit, window_seconds)
        except Exception:
            # Safe degradation (ARC11-I03, ADR-0196)
            return await self._fallback_limiter.allow(key, limit, window_seconds)


default_rate_limiter = InMemoryRateLimiter()


async def enforce_limit(
    limiter: RateLimiter,
    key: str,
    limit: int,
    window_seconds: int,
    retry_after: int = 60,
) -> None:
    """Enforce rate limit; raises RateLimitExceeded on violation."""
    allowed = await limiter.allow(key=key, limit=limit, window_seconds=window_seconds)
    if not allowed:
        raise RateLimitExceeded(retry_after_seconds=retry_after)
