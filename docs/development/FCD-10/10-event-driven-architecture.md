# FCD-10 — Event-Driven Architecture & Envelope Standards

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Event Envelope Specification

All domain events are encapsulated within `EventEnvelope` (`menu_it.platform.events.contracts`):
```python
@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: UUID
    event_type: str
    schema_version: int
    occurred_at: datetime
    organization_id: UUID | None
    actor_user_id: UUID | None
    correlation_id: str
    payload: dict[str, Any]
```

---

## 2. Standard Platform Domain Events

- `NotificationRequested`: Triggers multi-channel notification dispatch.
- `FileUploaded`: Triggers metadata extraction and storage processing.
- `UserRegistered`: Triggers account provisioning and welcome communications.
- `TenantCreated`: Triggers tenant provisioning and resource allocation.
