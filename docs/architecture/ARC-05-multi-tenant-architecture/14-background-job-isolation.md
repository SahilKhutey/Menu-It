# 14 — Background Job & Asynchronous Processing Isolation

## 1. TenantJobContext

```python
@dataclass(frozen=True)
class TenantJobContext:
    organization_id: UUID
    restaurant_id: Optional[UUID]
    initiating_user_id: Optional[UUID]
    correlation_id: str
    job_id: str
    purpose: str
```

## 2. Worker Lifecycle Safety

Workers running queued jobs:
1. Re-validate resource ownership against `job_ctx.organization_id`.
2. Apply transaction-scoped tenant context to the database session.
3. Clean up context unconditionally in a `finally` block before returning the process to the worker pool.
