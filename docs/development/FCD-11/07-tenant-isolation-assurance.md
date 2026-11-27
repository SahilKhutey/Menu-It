# FCD-11 · Document 07: Multi-Tenant Isolation & Data Boundary Assurance

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Dual-Layer Tenant Isolation Model

Menu-It enforces multi-tenant boundaries at two independent layers:

### Layer 1: Application-Level Scoping & Assertions
1. Inbound requests resolve the tenant via `TenantResolver` and produce an immutable `TenantContext`.
2. All repository queries filter by `organization_id == tenant_context.organization_id`.
3. Application services invoke `assert_tenant_boundary(resource_org_id, context_org_id)`. If an ID mismatch is detected, a `TenantAccessDeniedError` is raised immediately.

### Layer 2: PostgreSQL Row Level Security (RLS)
1. On acquiring a database connection, `set_database_tenant_context` runs:
   ```sql
   SELECT set_config('app.current_organization_id', :org_id, true);
   ```
2. PostgreSQL RLS policies enforce isolation on every tenant table:
   ```sql
   CREATE POLICY tenant_isolation_<table> ON <table>
   FOR ALL
   USING (
       organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
       OR organization_id IS NULL
   );
   ```
3. Even if application code has a logic bug, the database engine drops or refuses rows belonging to other organizations.
