# FCD-04 — Tenant Isolation & Repository Scoping

## 1. Multi-Layer Defense-in-Depth

Menu-It rejects single-point isolation models. Relying solely on application-level filtering risks accidental developer oversight, while relying solely on database RLS risks opaque query errors and un-indexed table scans.

Menu-It implements a **two-tier defense-in-depth model**:
1. **Application-Level Repository Isolation**: Programmatic filtering in `TenantScopedRepository[T]`.
2. **Database-Level Row-Level Security (RLS)**: PostgreSQL native policy enforcement using transaction-local configuration parameters.

---

## 2. The `TenantScopedRepository[ModelType]` Pattern

All tenant-owned repositories inherit from `TenantScopedRepository[ModelType]`.

```python
class TenantScopedRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, context: TenantContext):
        self.session = session
        self.context = context
        self.organization_id = context.organization_id
```

### Automatic Query Scoping
Every query automatically injects `where(self.model_class.organization_id == self.organization_id)`:
- **`get_by_id(id)`**: Fetches by `id` AND `organization_id`.
- **`list(offset, limit)`**: Restricts results strictly to the active tenant's records.
- **`create(entity)`**: Overrides `entity.organization_id = self.organization_id` before inserting, neutralizing any attempted client spoofing.
- **`update(id, values)`**: Executes updates filtered by `id` AND `organization_id`.
- **`delete(id)`**: Executes deletions filtered by `id` AND `organization_id`.

### Cross-Tenant Protection
If a user in Organization A calls `get_by_id(restaurant_b_id)`, the query evaluates:
```sql
SELECT * FROM restaurants
WHERE id = :restaurant_b_id AND organization_id = :org_a_id;
```
The result is `None` (not found), completely preventing cross-tenant reads or updates.
