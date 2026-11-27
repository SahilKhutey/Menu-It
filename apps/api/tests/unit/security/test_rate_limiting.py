"""Unit tests for sliding-window rate limiting adapter (FCD-05 §17.1)."""

from menu_it.security.rate_limiting import InMemoryRateLimiter


def test_rate_limiter_allows_under_limit():
    """Verify requests under maximum threshold are permitted."""
    limiter = InMemoryRateLimiter()
    key = "user-login-attempt-key"

    for _ in range(4):
        assert limiter.check_rate_limit(key, max_attempts=5, window_seconds=60) is True


def test_rate_limiter_blocks_over_limit():
    """Verify requests exceeding threshold are blocked."""
    limiter = InMemoryRateLimiter()
    key = "user-login-attempt-key-2"

    for _ in range(5):
        assert limiter.check_rate_limit(key, max_attempts=5, window_seconds=60) is True

    # 6th attempt should be blocked
    assert limiter.check_rate_limit(key, max_attempts=5, window_seconds=60) is False


def test_rate_limiter_reset():
    """Verify reset clears history for specified key."""
    limiter = InMemoryRateLimiter()
    key = "user-reset-key"

    for _ in range(3):
        limiter.check_rate_limit(key, max_attempts=3, window_seconds=60)

    assert limiter.check_rate_limit(key, max_attempts=3, window_seconds=60) is False
    limiter.reset(key)
    assert limiter.check_rate_limit(key, max_attempts=3, window_seconds=60) is True
