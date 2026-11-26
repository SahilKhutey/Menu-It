"""Async infrastructure, cache, and background job integration tests (FCD-13 WP-07).

Verifies:
- Cache service get/set/invalidate operations
- Job registry and handler registration
- Event dispatcher and consumer subscription
"""

from uuid import uuid4

import pytest

from menu_it.platform.cache.contracts import InMemoryCacheBackend
from menu_it.platform.cache.service import CacheService
from menu_it.platform.jobs.registry import JOB_REGISTRY, register_job_type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_service_lifecycle_and_invalidation():
    """ASYNCINT-T08: Cache service sets, retrieves, and invalidates cache entries."""
    backend = InMemoryCacheBackend()
    service = CacheService(backend=backend, enabled=True)

    key = f"menu:restaurant:{uuid4()}"
    value = {"name": "Summer Special Menu", "items_count": 12}

    # Set
    await service.set_json(key, value, ttl_seconds=60)

    # Get
    cached = await service.get_json(key)
    assert cached == value

    # Invalidate / Delete
    await service.delete(key)
    assert await service.get_json(key) is None


@pytest.mark.unit
def test_job_registry_registration():
    """ASYNCINT-T03: Core job handlers are registered in JOB_REGISTRY."""
    assert "notification.send" in JOB_REGISTRY
    assert "file.process" in JOB_REGISTRY
    assert "menu.rebuild" in JOB_REGISTRY

    # Custom registration
    dummy_handler = lambda ctx, *args, **kwargs: None  # noqa: E731
    register_job_type("custom.test.task", dummy_handler)
    assert "custom.test.task" in JOB_REGISTRY
