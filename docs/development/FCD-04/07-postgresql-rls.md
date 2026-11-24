# FCD-04 — PostgreSQL Row-Level Security (RLS) & Connection Isolation

## 1. Native Database Isolation

PostgreSQL Row-Level Security (RLS) acts as the final perimeter defense. Even if an application bug omitted a `WHERE organization_id` clause, or if a raw SQL statement bypassed the repository layer, PostgreSQL prevents unauthorized row access at the storage engine level.

---

## 2. Transaction-Local Tenant Context

In pooled environments (like SQLAlchemy connection pools or PgBouncer), setting global session variables (`SET session ...`) causes cross-request tenant leakage when connections are recycled.

Menu-It eliminates connection pool contamination by using **transaction-local settings**:

```python
async def set_database_tenant_context(
    session: AsyncSession,
    organization_id: UUID,
) -> None:
    if session.bind and session.bind.dialect.name == "postgresql":
        await session.execute(
            text("SELECT set_config('app.current_organization_id', :org_id, true)"),
            {"org_id": str(organization_id)},
        )
```

The third argument (`is_local=true`) instructs PostgreSQL to scope the setting strictly to the current transaction. As soon as the transaction completes (`COMMIT` or `ROLLBACK`), PostgreSQL automatically reverts the setting to null.

---

## 3. RLS Policies

Row-Level Security is enabled and enforced across all tenant-owned tables:
- `restaurants`
- `organization_memberships`
- `restaurant_memberships`
- `organization_audit_events`

### Policy Definition Pattern
```sql
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE restaurants FORCE ROW LEVEL SECURITY;

CREATE POLICY restaurants_tenant_isolation ON restaurants
USING (
    organization_id = NULLIF(
        current_setting('app.current_organization_id', true), ''
    )::uuid
)
WITH CHECK (
    organization_id = NULLIF(
        current_setting('app.current_organization_id', true), ''
    )::uuid
);
```

### Policy Semantics
1. **`FORCE ROW LEVEL SECURITY`**: Guarantees that table owners and migration roles are also constrained by RLS during regular runtime operations.
2. **`USING` clause**: Controls row visibility for `SELECT`, `UPDATE`, and `DELETE`.
3. **`WITH CHECK` clause**: Controls row validation for `INSERT` and `UPDATE`, rejecting records that attempt to write to another tenant.
4. **`current_setting('app.current_organization_id', true)`**: The `true` parameter prevents errors when the setting has not been initialized, returning `NULL` instead.
