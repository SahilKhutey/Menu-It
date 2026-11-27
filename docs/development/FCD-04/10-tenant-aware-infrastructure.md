# FCD-04 — Tenant-Aware Infrastructure Interfaces

## 1. Multi-Tenant Infrastructure Boundaries

Multi-tenant safety in Menu-It extends beyond relational tables into cache stores, object storage buckets, and asynchronous task queues. Infrastructure keys and prefixes must always be strictly namespaced by `organization_id`.

---

## 2. Object Storage Key Namespacing

Customer assets (restaurant logos, menu item photos, exported spreadsheets) share underlying S3/MinIO buckets. To prevent path traversal or cross-tenant overwrites, storage keys are strictly formatted via `format_tenant_storage_key`:

```python
def format_tenant_storage_key(
    organization_id: UUID,
    path: str,
    restaurant_id: UUID | None = None,
) -> str:
    clean_path = path.strip("/")
    if restaurant_id:
        return f"org_{organization_id}/rest_{restaurant_id}/{clean_path}"
    return f"org_{organization_id}/{clean_path}"
```

### Path Conventions
- **Organization Assets**: `org_{organization_id}/branding/logo.png`
- **Restaurant Assets**: `org_{organization_id}/rest_{restaurant_id}/menus/spring.pdf`

---

## 3. Cache Key Namespacing

Cache stores (e.g., Redis) hold frequently accessed menus and restaurant status flags. Keys must include the tenant boundary to prevent data collision:

```python
def format_tenant_cache_key(
    organization_id: UUID,
    key: str,
    restaurant_id: UUID | None = None,
) -> str:
    clean_key = key.strip(":")
    if restaurant_id:
        return f"org:{organization_id}:rest:{restaurant_id}:{clean_key}"
    return f"org:{organization_id}:{clean_key}"
```

---

## 4. Background Job Context (`TenantJobContext`)

Background workers executing outside HTTP request lifecycles (e.g. Celery / ARQ / Celery workers) must receive explicit tenant scope tokens:

```python
@dataclass(frozen=True, slots=True)
class TenantJobContext:
    organization_id: UUID
    job_id: str
    job_name: str
    triggered_by: str
    restaurant_id: UUID | None = None
    correlation_id: str | None = None

    def to_system_context(self) -> SystemTenantContext:
        return SystemTenantContext(
            organization_id=self.organization_id,
            system_actor=f"job:{self.job_name}",
            job_id=self.job_id,
            restaurant_id=self.restaurant_id,
            correlation_id=self.correlation_id,
        )
```

---

## 5. Organization Audit Logging

High-impact tenant actions (provisioning, status changes, member invitations, role changes) generate tamper-evident audit records in `organization_audit_events`:

```sql
CREATE TABLE organization_audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    actor_id UUID,
    event_type VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id UUID,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX ix_org_audit_org_created ON organization_audit_events (organization_id, created_at DESC);
```
