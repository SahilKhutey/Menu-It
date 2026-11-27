"""Cache platform package initialization (FCD-10 WP-02)."""

from menu_it.platform.cache.contracts import CacheBackend, InMemoryCacheBackend
from menu_it.platform.cache.keys import organization_key, public_key
from menu_it.platform.cache.policies import (
    DEFAULT_CACHE_TTL,
    TTL_LONG,
    TTL_MEDIUM,
    TTL_SHORT,
    TTL_VERY_LONG,
)
from menu_it.platform.cache.service import CacheService

__all__ = [
    "CacheBackend",
    "InMemoryCacheBackend",
    "CacheService",
    "organization_key",
    "public_key",
    "DEFAULT_CACHE_TTL",
    "TTL_SHORT",
    "TTL_MEDIUM",
    "TTL_LONG",
    "TTL_VERY_LONG",
]
