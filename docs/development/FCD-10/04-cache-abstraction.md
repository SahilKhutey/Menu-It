# FCD-10 — Cache Abstraction & Adapters

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Provider-Independent Cache Contract

The platform defines `CacheBackend` Protocol in `menu_it.platform.cache.contracts`:
```python
class CacheBackend(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, ttl_seconds: int) -> None: ...
    async def delete(self, key: str) -> None: ...
    async def delete_pattern(self, pattern: str) -> int: ...
    async def exists(self, key: str) -> bool: ...
```

---

## 2. Implementations

1. **`RedisCacheBackend` (`menu_it.infrastructure.redis.cache_backend`):**
   - Asynchronous Redis commands via `redis.asyncio.Redis`.
   - Pattern deletion uses `scan_iter(count=200)` to prevent blocking the Redis event loop.
   - Comprehensive error suppression: Redis connection outages log warnings and return `None` rather than failing user requests.
2. **`InMemoryCacheBackend` (`menu_it.platform.cache.contracts`):**
   - Thread-safe dictionary storing `(value, expires_at)`.
   - Supports glob pattern matching via `fnmatch`.
   - Enables fast, zero-dependency unit and CI testing.
