"""Redis cache backend implementation (FCD-10 WP-02)."""

import logging

from redis.asyncio import Redis

logger = logging.getLogger("menu_it.infrastructure.redis.cache")


class RedisCacheBackend:
    """Redis-backed implementation of CacheBackend protocol."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> bytes | None:
        """Retrieve raw cached bytes by key."""
        try:
            return await self.redis.get(key)
        except Exception as exc:
            logger.warning(f"Redis get failed for key '{key}': {exc}")
            return None

    async def set(
        self,
        key: str,
        value: bytes,
        ttl_seconds: int,
    ) -> None:
        """Store raw bytes in cache with mandatory positive TTL."""
        if ttl_seconds <= 0:
            raise ValueError("Cache TTL must be strictly greater than zero seconds.")
        try:
            await self.redis.set(key, value, ex=ttl_seconds)
        except Exception as exc:
            logger.warning(f"Redis set failed for key '{key}': {exc}")

    async def delete(self, key: str) -> None:
        """Remove a single cache key."""
        try:
            await self.redis.delete(key)
        except Exception as exc:
            logger.warning(f"Redis delete failed for key '{key}': {exc}")

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a pattern via SCAN to avoid blocking Redis."""
        deleted = 0
        try:
            keys_to_delete = []
            async for key in self.redis.scan_iter(match=pattern, count=200):
                keys_to_delete.append(key)
                if len(keys_to_delete) >= 200:
                    deleted += await self.redis.delete(*keys_to_delete)
                    keys_to_delete.clear()
            if keys_to_delete:
                deleted += await self.redis.delete(*keys_to_delete)
        except Exception as exc:
            logger.warning(f"Redis delete_pattern failed for pattern '{pattern}': {exc}")
        return deleted

    async def exists(self, key: str) -> bool:
        """Check whether key exists in Redis."""
        try:
            return bool(await self.redis.exists(key))
        except Exception as exc:
            logger.warning(f"Redis exists failed for key '{key}': {exc}")
            return False
