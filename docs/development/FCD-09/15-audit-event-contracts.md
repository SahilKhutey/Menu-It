# FCD-09 §15 — Audit Event Contracts

## 1. Audit Event Contract

Menu-It defines a canonical `AuditEvent` dataclass in `menu_it.platform.audit.contracts`:

```python
@dataclass(frozen=True)
class AuditEvent:
    event_id: UUID
    event_type: str
    occurred_at: datetime
    organization_id: UUID | None
    actor_user_id: UUID | None
    resource_type: str
    resource_id: str | None
    action: str
    outcome: str
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

---

## 2. Standard Event Catalog

- `file.uploaded`: File uploaded and persisted.
- `file.deleted`: File soft-deleted.
- `notification.requested`: Outbound notification dispatched.
- `notification.failed`: Notification delivery failed.
- `config.changed`: Runtime configuration updated.

---

## 3. Audit Publishers

- **`InMemoryAuditEventPublisher`:** Retains events in an in-memory list for test verification.
- **`LoggingAuditEventPublisher`:** Dispatches structured audit logs to the application logger with `AUDIT_EVENT` prefixes.
- **Future Durable Publisher (FCD-11):** Sinks audit events to dedicated append-only compliance databases.
