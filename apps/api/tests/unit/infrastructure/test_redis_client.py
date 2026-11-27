"""Unit tests for Redis connection lifecycle and client creation (FCD-10 WP-01)."""

import pytest

from menu_it.core.config import Settings
from menu_it.infrastructure.redis.client import (
    close_redis_client,
    create_redis_client,
    create_redis_pool,
)


def test_create_redis_pool_and_client():
    settings = Settings(
        redis_url="redis://localhost:6379/1",
        redis_max_connections=15,
        redis_connect_timeout=3,
        redis_socket_timeout=3,
    )
    pool = create_redis_pool(settings)
    assert pool.max_connections == 15
    assert pool.connection_kwargs["socket_connect_timeout"] == 3

    client = create_redis_client(pool=pool)
    assert client.connection_pool is pool


@pytest.mark.asyncio
async def test_close_redis_client_handles_none_and_exceptions():
    # Should safely no-op when None
    await close_redis_client(None)

    # Should safely handle client close
    settings = Settings()
    client = create_redis_client(settings=settings)
    await close_redis_client(client)
