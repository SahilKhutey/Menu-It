"""Tests for rate limiting implementations (FCD-11 WP-06)."""

import pytest

from menu_it.platform.security.rate_limit import (
    InMemoryRateLimiter,
    RedisRateLimiter,
)


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_allows_under_quota() -> None:
    limiter = InMemoryRateLimiter()
    key = "tenant:org-1"

    # 3 allowed requests within 60 second window
    res1 = await limiter.check_rate_limit(key, limit=3, window_seconds=60)
    assert res1.allowed is True
    assert res1.remaining == 2

    res2 = await limiter.check_rate_limit(key, limit=3, window_seconds=60)
    assert res2.allowed is True
    assert res2.remaining == 1

    res3 = await limiter.check_rate_limit(key, limit=3, window_seconds=60)
    assert res3.allowed is True
    assert res3.remaining == 0


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_blocks_over_quota() -> None:
    limiter = InMemoryRateLimiter()
    key = "tenant:org-2"

    for _ in range(2):
        res = await limiter.check_rate_limit(key, limit=2, window_seconds=60)
        assert res.allowed is True

    # 3rd request must be rejected
    blocked = await limiter.check_rate_limit(key, limit=2, window_seconds=60)
    assert blocked.allowed is False
    assert blocked.remaining == 0
    assert blocked.retry_after > 0


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_reset() -> None:
    limiter = InMemoryRateLimiter()
    key = "tenant:org-3"

    await limiter.check_rate_limit(key, limit=1, window_seconds=60)
    blocked = await limiter.check_rate_limit(key, limit=1, window_seconds=60)
    assert blocked.allowed is False

    await limiter.reset(key)
    allowed_again = await limiter.check_rate_limit(key, limit=1, window_seconds=60)
    assert allowed_again.allowed is True


@pytest.mark.asyncio
async def test_redis_rate_limiter_fallback() -> None:
    # When redis client is None, RedisRateLimiter falls back gracefully to InMemoryRateLimiter
    limiter = RedisRateLimiter(redis_client=None)
    res = await limiter.check_rate_limit("test-key", limit=5, window_seconds=10)
    assert res.allowed is True
    assert res.remaining == 4
