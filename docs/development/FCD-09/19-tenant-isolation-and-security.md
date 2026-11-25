# FCD-09 §19 — Tenant Isolation & Security

## 1. Defense-in-Depth Tenant Isolation

Platform services enforce tenant isolation through five coordinated layers:

1. **Authentication Boundary:** Only verified JWT bearer tokens resolve an active `AuthenticatedPrincipal`.
2. **Server-Derived Tenancy:** Organization membership and roles are resolved server-side from `TenantResolver`, not from arbitrary request-body parameters.
3. **Application Service Authorization:** `FileService` verifies that `current_org_id == metadata.organization_id` before returning private content or metadata.
4. **PostgreSQL Row-Level Security:** Database-level security policies filter `files` and `notifications` using `app.current_organization_id`.
5. **Path Traversal Defense:** Storage adapters constrain all read and write operations strictly within the root directory.

---

## 2. File Access Gates

- Public files can be viewed by anyone without authentication.
- Tenant-private files require valid organization membership.
- User-private files require ownership by the authenticated user.
- Platform-private files require platform administrative privileges.
