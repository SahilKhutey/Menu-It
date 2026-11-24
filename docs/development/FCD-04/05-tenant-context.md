# FCD-04 — Immutable TenantContext & ContextVar Lifecycle

## 1. Immutable TenantContext Contract

The `TenantContext` is the canonical runtime token representing the active tenant and operating user. It is implemented as a frozen dataclass with slots to prevent modification or dynamic attribute injection during request processing.

```python
@dataclass(frozen=True, slots=True)
class TenantContext:
    organization_id: UUID
    user_id: UUID
    organization_role: str
    restaurant_id: UUID | None = None
    restaurant_role: str | None = None
    correlation_id: str | None = None
```

### Invariants
- **Read-Only**: Any attempt to modify fields (e.g., `tenant.organization_id = other_id`) raises a `FrozenInstanceError`.
- **Slotted Attributes**: Prevents arbitrary runtime tampering or state leakage between components.
- **Traceability**: Contains `correlation_id` matching `X-Request-ID` for cross-service logging and tracing.

---

## 2. Asynchronous ContextVar Management

To guarantee isolation across concurrent async requests without thread-local pollution, Menu-It manages tenant state using Python's `contextvars`:

```python
_current_tenant_ctx: ContextVar[TenantContext | None] = ContextVar(
    "current_tenant_ctx",
    default=None,
)
```

### Lifecycle Functions
- **`set_current_tenant(context: TenantContext) -> Token`**: Stores the verified context and returns an opaque reset token.
- **`get_current_tenant() -> TenantContext`**: Returns the active context; raises `TenantContextMissingError` if called outside an authenticated tenant scope.
- **`reset_current_tenant(token: Token) -> None`**: Restores the previous contextvar state in a `finally` block, ensuring no context leaks into subsequent pooled coroutines or worker threads.

---

## 3. Background Job & System Tenant Context

Asynchronous background tasks, queues, or scheduled automations do not have an interactive user principal. For these operations, Menu-It provides `SystemTenantContext`:

```python
@dataclass(frozen=True, slots=True)
class SystemTenantContext:
    organization_id: UUID
    system_actor: str
    job_id: str
    restaurant_id: UUID | None = None
    correlation_id: str | None = None
```

This ensures background tasks always execute with an explicit tenant scope, preventing multi-tenant data corruption in async workers.
