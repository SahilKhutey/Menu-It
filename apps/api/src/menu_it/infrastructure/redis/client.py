"""Redis client connection management and lifecycle (FCD-10 WP-01)."""

import logging

from menu_it.core.config import Settings, get_settings
from redis.asyncio import ConnectionPool, Redis

logger = logging.getLogger("menu_it.infrastructure.redis")


def create_redis_pool(settings: Settings | None = None) -> ConnectionPool:
    """Create a managed asynchronous Redis connection pool."""
    cfg = settings or get_settings()
    return ConnectionPool.from_url(
        cfg.redis_url,
        decode_responses=False,
        max_connections=cfg.redis_max_connections,
        socket_connect_timeout=cfg.redis_connect_timeout,
        socket_timeout=cfg.redis_socket_timeout,
        health_check_interval=30,
    )


def create_redis_client(
    pool: ConnectionPool | None = None,
    settings: Settings | None = None,
) -> Redis:
    """Create an asynchronous Redis client bound to a connection pool."""
    if pool is not None:
        return Redis(connection_pool=pool)
    connection_pool = create_redis_pool(settings)
    return Redis(connection_pool=connection_pool)


async def close_redis_client(redis: Redis | None) -> None:
    """Safely terminate Redis client connections."""
    if redis is None:
        return
    try:
        await redis.aclose()
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Error while closing Redis client: {exc}")
