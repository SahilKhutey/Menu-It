"""Centralized high-level CacheService (FCD-10 WP-02)."""

import json
import logging
from typing import Any
from uuid import UUID

from menu_it.platform.cache.contracts import CacheBackend
from menu_it.platform.cache.policies import DEFAULT_CACHE_TTL
from menu_it.platform.cache.serialization import (
    deserialize_from_cache,
    serialize_for_cache,
)

logger = logging.getLogger("menu_it.platform.cache.service")


class CacheService:
    """Application cache service providing typed JSON caching and safe failure handling."""

    def __init__(self, backend: CacheBackend, enabled: bool = True) -> None:
        self.backend = backend
        self.enabled = enabled

    async def get_json(self, key: str) -> Any | None:
        """Retrieve and parse JSON cached object by key."""
        if not self.enabled:
            return None
        try:
            raw = await self.backend.get(key)
            if raw is None:
                return None
            return deserialize_from_cache(raw)
        except (ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning(f"Corrupted cache entry for key '{key}', removing: {exc}")
            await self.backend.delete(key)
            return None
        except Exception as exc:
            logger.warning(f"Cache get_json failed for key '{key}': {exc}")
            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = DEFAULT_CACHE_TTL,
    ) -> None:
        """Serialize and store an object as JSON with TTL."""
        if not self.enabled:
            return
        try:
            payload = serialize_for_cache(value)
            await self.backend.set(key, payload, ttl_seconds=ttl_seconds)
        except Exception as exc:
            logger.warning(f"Cache set_json failed for key '{key}': {exc}")

    async def delete(self, key: str) -> None:
        """Delete an individual cache key."""
        if not self.enabled:
            return
        try:
            await self.backend.delete(key)
        except Exception as exc:
            logger.warning(f"Cache delete failed for key '{key}': {exc}")

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a glob pattern."""
        if not self.enabled:
            return 0
        try:
            return await self.backend.delete_pattern(pattern)
        except Exception as exc:
            logger.warning(f"Cache delete_pattern failed for pattern '{pattern}': {exc}")
            return 0

    async def invalidate_organization_resource(
        self,
        organization_id: UUID,
        resource: str,
    ) -> int:
        """Invalidate all cached keys for an organization's specific resource."""
        pattern = f"menu-it:v1:org:{organization_id}:{resource}:*"
        return await self.delete_pattern(pattern)

    async def exists(self, key: str) -> bool:
        """Check whether key exists in cache."""
        if not self.enabled:
            return False
        try:
            return await self.backend.exists(key)
        except Exception as exc:
            logger.warning(f"Cache exists failed for key '{key}': {exc}")
            return False
