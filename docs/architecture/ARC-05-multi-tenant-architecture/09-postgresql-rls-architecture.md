# 09 — PostgreSQL Row-Level Security (RLS) Architecture

## 1. Defense-in-Depth Implementation

PostgreSQL RLS acts as a hardware-level safety net beneath the application layer.

```sql
ALTER TABLE menus ENABLE ROW LEVEL SECURITY;
ALTER TABLE menus FORCE ROW LEVEL SECURITY;

CREATE POLICY menus_tenant_isolation
ON menus
AS RESTRICTIVE
USING (
    organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
)
WITH CHECK (
    organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
);
```

## 2. Transaction Locality

The context is established per transaction:
`SELECT set_config('app.current_organization_id', :org_id, true);`

The `is_local=true` parameter ensures that as soon as the transaction completes (COMMIT or ROLLBACK), the setting is automatically cleared, preventing connection pool contamination.
