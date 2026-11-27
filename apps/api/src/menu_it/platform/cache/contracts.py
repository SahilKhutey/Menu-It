"""Cache backend protocol contracts and in-memory test adapter (FCD-10 WP-02)."""

import fnmatch
import time
from typing import Protocol


class CacheBackend(Protocol):
    """Protocol for provider-agnostic caching implementations."""

    async def get(self, key: str) -> bytes | None:
        """Retrieve raw cached bytes by key."""
        ...

    async def set(
        self,
        key: str,
        value: bytes,
        ttl_seconds: int,
    ) -> None:
        """Store raw bytes in cache with mandatory positive TTL."""
        ...

    async def delete(self, key: str) -> None:
        """Remove a single cache key."""
        ...

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching the glob pattern."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if a cache key exists."""
        ...


class InMemoryCacheBackend:
    """In-memory cache backend with TTL support for testing and local fallback."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[bytes, float | None]] = {}

    def _purge_expired(self, key: str) -> bool:
        """Purge key if expired. Returns True if expired."""
        if key not in self._store:
            return True
        val, expires_at = self._store[key]
        if expires_at is not None and time.monotonic() > expires_at:
            del self._store[key]
            return True
        return False

    async def get(self, key: str) -> bytes | None:
        if self._purge_expired(key):
            return None
        return self._store[key][0]

    async def set(
        self,
        key: str,
        value: bytes,
        ttl_seconds: int,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("Cache TTL must be strictly greater than zero seconds.")
        expires_at = time.monotonic() + ttl_seconds
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def delete_pattern(self, pattern: str) -> int:
        keys_to_delete = [k for k in list(self._store.keys()) if fnmatch.fnmatch(k, pattern)]
        count = 0
        for k in keys_to_delete:
            del self._store[k]
            count += 1
        return count

    async def exists(self, key: str) -> bool:
        if self._purge_expired(key):
            return False
        return key in self._store

    def clear(self) -> None:
        """Synchronously clear all in-memory entries."""
        self._store.clear()
