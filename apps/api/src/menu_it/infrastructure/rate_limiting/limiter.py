"""Rate limiter implementations for API rate limiting (FCD-07 WP-10)."""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RateLimitResult:
    """Outcome of a rate limit evaluation."""

    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int


class RateLimiter(Protocol):
    """Abstract rate limiter protocol."""

    async def check_and_consume(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        """Evaluate and consume a rate limit token for a key."""
        ...


class InMemoryRateLimiter:
    """Thread-safe and async-safe in-memory sliding window rate limiter."""

    def __init__(self) -> None:
        self._history: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check_and_consume(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        """Evaluate key against sliding window."""
        async with self._lock:
            now = time.monotonic()
            threshold = now - window_seconds
            timestamps = self._history[key]

            # Prune expired timestamps
            while timestamps and timestamps[0] <= threshold:
                timestamps.popleft()

            if len(timestamps) < limit:
                timestamps.append(now)
                remaining = limit - len(timestamps)
                # Reset time until the oldest token expires
                reset_seconds = (
                    int(window_seconds - (now - timestamps[0])) if timestamps else window_seconds
                )
                return RateLimitResult(
                    allowed=True,
                    limit=limit,
                    remaining=max(0, remaining),
                    reset_seconds=max(1, reset_seconds),
                )

            # Limit exceeded
            reset_seconds = int(window_seconds - (now - timestamps[0]))
            return RateLimitResult(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_seconds=max(1, reset_seconds),
            )

    async def reset(self, key: str | None = None) -> None:
        """Clear recorded requests for a specific key or all keys."""
        async with self._lock:
            if key is not None:
                self._history.pop(key, None)
            else:
                self._history.clear()


class RedisRateLimiter:
    """Redis-backed sliding window rate limiter with in-memory fallback."""

    def __init__(self, redis_client=None, fallback: InMemoryRateLimiter | None = None) -> None:
        self._redis = redis_client
        self._fallback = fallback or InMemoryRateLimiter()

    async def check_and_consume(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> RateLimitResult:
        """Evaluate rate limit in Redis or fall back to in-memory."""
        if self._redis is None:
            return await self._fallback.check_and_consume(key, limit, window_seconds)

        try:
            now = time.time()
            threshold = now - window_seconds
            redis_key = f"rate_limit:{key}"

            pipeline = self._redis.pipeline()
            pipeline.zremrangebyscore(redis_key, 0, threshold)
            pipeline.zcard(redis_key)
            pipeline.zadd(redis_key, {str(now): now})
            pipeline.expire(redis_key, window_seconds + 5)
            results = await pipeline.execute()

            count = results[1]
            if count < limit:
                remaining = limit - count - 1
                return RateLimitResult(
                    allowed=True,
                    limit=limit,
                    remaining=max(0, remaining),
                    reset_seconds=window_seconds,
                )

            return RateLimitResult(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_seconds=window_seconds,
            )
        except Exception:
            # Fallback to local memory on Redis failure
            return await self._fallback.check_and_consume(key, limit, window_seconds)


# Default global rate limiter instance
default_rate_limiter = InMemoryRateLimiter()
