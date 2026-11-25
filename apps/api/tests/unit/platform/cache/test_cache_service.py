"""Unit tests for CacheService, keys, and InMemoryCacheBackend (FCD-10 WP-02)."""

import asyncio
import uuid
import pytest

from menu_it.platform.cache import (
    CacheService,
    InMemoryCacheBackend,
    organization_key,
    public_key,
)
from menu_it.platform.cache.contracts import CacheBackend


@pytest.fixture
def cache_service() -> CacheService:
    backend = InMemoryCacheBackend()
    return CacheService(backend=backend)


@pytest.mark.asyncio
async def test_cac_01_read_missing_key_returns_none(cache_service: CacheService):
    result = await cache_service.get_json("menu-it:v1:test:missing")
    assert result is None


@pytest.mark.asyncio
async def test_cac_02_write_then_read_returns_original_value(cache_service: CacheService):
    key = "menu-it:v1:test:sample"
    data = {"id": str(uuid.uuid4()), "name": "Bistro Menu", "items_count": 42}
    await cache_service.set_json(key, data, ttl_seconds=30)

    cached = await cache_service.get_json(key)
    assert cached == data


@pytest.mark.asyncio
async def test_cac_03_expired_key_returns_miss(cache_service: CacheService):
    key = "menu-it:v1:test:expiring"
    # Set with 0.01s TTL simulation via direct backend
    await cache_service.set_json(key, {"value": "fast"}, ttl_seconds=1)
    # Fast-forward expiry
    cache_service.backend._store[key] = (b'{"value":"fast"}', 0.0)

    cached = await cache_service.get_json(key)
    assert cached is None


@pytest.mark.asyncio
async def test_cac_04_delete_key(cache_service: CacheService):
    key = "menu-it:v1:test:to-delete"
    await cache_service.set_json(key, "hello", ttl_seconds=60)
    assert await cache_service.exists(key) is True

    await cache_service.delete(key)
    assert await cache_service.exists(key) is False
    assert await cache_service.get_json(key) is None


@pytest.mark.asyncio
async def test_cac_05_corrupted_json_removed(cache_service: CacheService):
    key = "menu-it:v1:test:corrupt"
    # Store corrupted non-JSON bytes directly in backend
    await cache_service.backend.set(key, b"{invalid-json-payload", ttl_seconds=60)

    result = await cache_service.get_json(key)
    assert result is None
    # Key should have been purged upon encountering corruption
    assert await cache_service.exists(key) is False


@pytest.mark.asyncio
async def test_cac_06_ttl_of_zero_or_less_rejected(cache_service: CacheService):
    with pytest.raises(ValueError, match="strictly greater than zero"):
        await cache_service.backend.set("key", b"val", ttl_seconds=0)

    with pytest.raises(ValueError, match="strictly greater than zero"):
        await cache_service.backend.set("key", b"val", ttl_seconds=-5)


def test_cac_07_and_08_organization_cache_key_isolation():
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()
    item_id = "menu-456"

    key_a = organization_key(org_a, "menus", item_id)
    key_b = organization_key(org_b, "menus", item_id)

    assert key_a != key_b
    assert str(org_a) in key_a
    assert str(org_b) in key_b
    assert str(org_b) not in key_a


def test_cache_keys_validation():
    org_id = uuid.uuid4()
    with pytest.raises(ValueError, match="Invalid resource namespace"):
        organization_key(org_id, "invalid:resource", "id")

    with pytest.raises(ValueError, match="Invalid resource identifier"):
        organization_key(org_id, "resource", "invalid:id")

    pub_key = public_key("menu", "bistro-slug")
    assert pub_key == "menu-it:v1:public:menu:bistro-slug"


@pytest.mark.asyncio
async def test_cac_09_and_10_cache_backend_failures_handled_gracefully():
    class FailingBackend(CacheBackend):
        async def get(self, key: str) -> bytes | None:
            raise ConnectionError("Redis unreachable")

        async def set(self, key: str, value: bytes, ttl_seconds: int) -> None:
            raise ConnectionError("Redis unreachable")

        async def delete(self, key: str) -> None:
            raise ConnectionError("Redis unreachable")

        async def delete_pattern(self, pattern: str) -> int:
            raise ConnectionError("Redis unreachable")

        async def exists(self, key: str) -> bool:
            raise ConnectionError("Redis unreachable")

    service = CacheService(backend=FailingBackend())

    # Get should return None instead of raising
    assert await service.get_json("any-key") is None
    # Set, delete, exists should safely catch and not raise
    await service.set_json("any-key", {"a": 1})
    await service.delete("any-key")
    assert await service.exists("any-key") is False


@pytest.mark.asyncio
async def test_cac_12_invalidate_organization_resource(cache_service: CacheService):
    org_id = uuid.uuid4()
    key_1 = organization_key(org_id, "menus", "menu-1")
    key_2 = organization_key(org_id, "menus", "menu-2")
    key_other_resource = organization_key(org_id, "profiles", "prof-1")
    key_other_org = organization_key(uuid.uuid4(), "menus", "menu-1")

    await cache_service.set_json(key_1, "menu1", ttl_seconds=60)
    await cache_service.set_json(key_2, "menu2", ttl_seconds=60)
    await cache_service.set_json(key_other_resource, "prof1", ttl_seconds=60)
    await cache_service.set_json(key_other_org, "other-org-menu", ttl_seconds=60)

    deleted_count = await cache_service.invalidate_organization_resource(org_id, "menus")
    assert deleted_count == 2

    # Menus for org_id deleted
    assert await cache_service.get_json(key_1) is None
    assert await cache_service.get_json(key_2) is None

    # Other resource and other org preserved
    assert await cache_service.get_json(key_other_resource) == "prof1"
    assert await cache_service.get_json(key_other_org) == "other-org-menu"
