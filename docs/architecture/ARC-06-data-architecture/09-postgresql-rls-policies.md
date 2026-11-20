# 09 — PostgreSQL Row-Level Security Policies

## 1. Policy Implementation

Every tenant-owned table enforces:
```sql
ALTER TABLE menus ENABLE ROW LEVEL SECURITY;
ALTER TABLE menus FORCE ROW LEVEL SECURITY;

CREATE POLICY menus_tenant_isolation
ON menus
AS RESTRICTIVE
USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid)
WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid);
```

## 2. Fail-Closed Guarantees

If `app.current_organization_id` is empty, unset, or corrupted, the policy evaluates to `NULL` and yields `0` rows.
