# FCD-09 §17 — Service Registration & Lifecycle

## 1. Platform Composition Root

`apps/api/src/menu_it/platform/container.py` acts as the composition root for platform services:

```python
@dataclass(frozen=True)
class PlatformServices:
    settings: Settings
    clock: Clock
    file_storage: FileStorage
    notification_service: NotificationService
    audit_publisher: AuditEventPublisher
```

---

## 2. Application Lifespan Integration

During application startup in `apps/api/src/menu_it/core/lifecycle.py`:
1. `build_platform_services()` initializes singletons (LocalFileStorage, TemplateRenderer, LoggingAuditEventPublisher).
2. The container is attached to `application.state.platform_services`.
3. `application.state.runtime_ready = True` marks readiness.
4. During shutdown, database connections and resources are safely disposed.
