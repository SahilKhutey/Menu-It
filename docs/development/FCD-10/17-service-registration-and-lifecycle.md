# FCD-10 — Service Registration & Application Lifecycle

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Composition Root (`menu_it.platform.container`)

The `PlatformServices` container aggregates:
- `settings: Settings`
- `clock: Clock`
- `file_storage: FileStorage`
- `notification_service: NotificationService`
- `audit_publisher: AuditEventPublisher`
- `cache_service: CacheService` (configured with `RedisCacheBackend` or `InMemoryCacheBackend`)

---

## 2. Application Lifespan Wiring

`initialize_runtime()` in `menu_it.core.lifecycle`:
- Builds `platform_services` singleton.
- Sets `application.state.platform_services`.
- Sets `application.state.runtime_ready = True`.

`shutdown_runtime()`:
- Disposes database engine.
- Closes Redis connection pool.
