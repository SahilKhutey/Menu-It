"""Unit tests for sliding window rate limiter (FCD-07 WP-10)."""

import pytest

from menu_it.infrastructure.rate_limiting.limiter import InMemoryRateLimiter


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_allowed_within_limit():
    limiter = InMemoryRateLimiter()
    key = "test-key-1"

    res1 = await limiter.check_and_consume(key, limit=2, window_seconds=60)
    assert res1.allowed
    assert res1.remaining == 1

    res2 = await limiter.check_and_consume(key, limit=2, window_seconds=60)
    assert res2.allowed
    assert res2.remaining == 0


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_blocks_when_exceeded():
    limiter = InMemoryRateLimiter()
    key = "test-key-2"

    await limiter.check_and_consume(key, limit=2, window_seconds=60)
    await limiter.check_and_consume(key, limit=2, window_seconds=60)

    res3 = await limiter.check_and_consume(key, limit=2, window_seconds=60)
    assert not res3.allowed
    assert res3.remaining == 0
    assert res3.reset_seconds > 0


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_reset():
    limiter = InMemoryRateLimiter()
    key = "test-key-3"

    await limiter.check_and_consume(key, limit=1, window_seconds=60)
    blocked = await limiter.check_and_consume(key, limit=1, window_seconds=60)
    assert not blocked.allowed

    await limiter.reset(key)
    allowed_again = await limiter.check_and_consume(key, limit=1, window_seconds=60)
    assert allowed_again.allowed
