# FCD-10 — Tenant-Context Propagation & Worker Security

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Security Invariants for Background Execution

1. **Explicit Context:** Every tenant-scoped job must carry a validated `JobContext(organization_id, actor_user_id, correlation_id, initiated_by)`.
2. **Transaction-Local PostgreSQL RLS:** When a worker claims a tenant-scoped job, it sets PostgreSQL transaction-local setting via `set_database_tenant_context(session, context)` executing `SELECT set_config('app.current_organization_id', :org_id, true)`.
3. **Zero Context Leakage:** Workers never reuse sessions across jobs. The transaction-local setting is cleared upon commit or rollback.
4. **Platform Operations:** Platform-level jobs explicitly carry `organization_id = None`. A `None` organization ID never grants access to all tenant data; it restricts access to platform-scoped tables only.
