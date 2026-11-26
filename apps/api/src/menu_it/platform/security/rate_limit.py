"""Distributed and in-memory rate limiting engine (FCD-11 WP-06)."""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RateLimitResult:
    """Outcome of a rate limit check."""

    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int
    retry_after: int = 0


class RateLimitExceededException(Exception):
    """Raised when an operation or request exceeds its assigned rate quota."""

    def __init__(self, result: RateLimitResult, message: str = "Rate limit exceeded") -> None:
        self.result = result
        super().__init__(f"{message}. Retry after {result.retry_after} seconds.")


@runtime_checkable
class RateLimiter(Protocol):
    """Protocol defining rate limiter behavior."""

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        """Check whether key has exceeded quota in the sliding window."""
        ...


class InMemoryRateLimiter:
    """Sliding-window in-memory rate limiter using monotonic timestamps."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        async with self._lock:
            now = time.time()
            cutoff = now - window_seconds

            # Filter out entries older than current sliding window
            timestamps = [t for t in self._hits[key] if t > cutoff]

            if len(timestamps) >= limit:
                # Quota exceeded
                oldest = timestamps[0] if timestamps else now
                retry_after = max(1, int(oldest + window_seconds - now))
                reset_seconds = retry_after
                self._hits[key] = timestamps
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    reset_seconds=reset_seconds,
                    retry_after=retry_after,
                )

            # Record this hit
            timestamps.append(now)
            self._hits[key] = timestamps
            remaining = max(0, limit - len(timestamps))
            reset_seconds = max(1, int(timestamps[0] + window_seconds - now))

            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=remaining,
                reset_seconds=reset_seconds,
                retry_after=0,
            )

    async def reset(self, key: str | None = None) -> None:
        """Reset hit counters for testing or maintenance."""
        async with self._lock:
            if key is not None:
                self._hits.pop(key, None)
            else:
                self._hits.clear()


class RedisRateLimiter:
    """Distributed Redis-backed sliding-window rate limiter with in-memory fallback."""

    def __init__(
        self,
        redis_client: Any | None = None,
        *,
        fallback_limiter: RateLimiter | None = None,
        prefix: str = "menu_it:ratelimit:",
    ) -> None:
        self.redis = redis_client
        self.prefix = prefix
        self.fallback = fallback_limiter or InMemoryRateLimiter()

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        full_key = f"{self.prefix}{key}"
        now = time.time()
        cutoff = now - window_seconds

        if self.redis is None:
            return await self.fallback.check_rate_limit(key, limit, window_seconds)

        try:
            pipe = self.redis.pipeline()
            # Remove timestamps outside current window
            pipe.zremrangebyscore(full_key, 0, cutoff)
            # Count remaining items
            pipe.zcard(full_key)
            # Add current hit
            pipe.zadd(full_key, {str(now): now})
            # Set key expiration
            pipe.expire(full_key, window_seconds + 5)
            # Get earliest timestamp in window for reset calculation
            pipe.zrange(full_key, 0, 0, withscores=True)

            results = await pipe.execute()
            current_count = results[1]
            earliest = results[4]

            if current_count >= limit:
                # Quota exceeded; roll back the hit we just added
                await self.redis.zrem(full_key, str(now))
                earliest_ts = earliest[0][1] if earliest else now
                retry_after = max(1, int(earliest_ts + window_seconds - now))
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    reset_seconds=retry_after,
                    retry_after=retry_after,
                )

            remaining = max(0, limit - (current_count + 1))
            earliest_ts = earliest[0][1] if earliest else now
            reset_seconds = max(1, int(earliest_ts + window_seconds - now))

            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=remaining,
                reset_seconds=reset_seconds,
                retry_after=0,
            )

        except Exception as exc:
            logger.warning(
                "Redis rate limiting failed; degrading to in-memory fallback: %s",
                exc,
            )
            return await self.fallback.check_rate_limit(key, limit, window_seconds)
