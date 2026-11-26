# FCD-11 · Document 06: Authorization & Access Control Enforcement

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Deny-by-Default Authorization Engine

Menu-It uses a role-based access control (RBAC) model augmented with resource-level permission assertions:

- **Roles:** `owner`, `admin`, `manager`, `staff`.
- **Permissions:** Granular domain verbs (e.g. `restaurant:read`, `restaurant:write`, `menu:item:create`, `order:process`).
- **Assertion Helpers:** `require_permission(available_permissions, required_permission)`
  - Exact match (`restaurant:read` in permissions).
  - Domain wildcards (`restaurant:*` grants `restaurant:read` and `restaurant:write`).
  - Superuser wildcards (`*` or `admin`).
  - Missing permissions immediately raise `PermissionDeniedError` returning HTTP 403 Forbidden.

---

## 2. Platform Admin vs Tenant User Segregation

- Platform operators belong to `platform_memberships` (FCD-05 §12) and operate in a distinct security domain from tenant members (`organization_memberships`).
- Tenant users cannot invoke platform administration endpoints.
- Any attempt to access unauthorized platform endpoints records a `security_audit_events` row with `outcome='denied'`.
