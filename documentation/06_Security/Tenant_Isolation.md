# Multi-Tenant Isolation & Security Specification
**Document ID:** SEC-TENANT-001  
**Security Level:** Critical (P0 Production Gate)

---

## 1. Threat Model & Defense-in-Depth Strategy

Because multiple restaurants share the same PostgreSQL database in the Managed SaaS edition, multi-tenant isolation must be enforced with zero room for error. ModularMenu employs three independent layers of isolation:

```
+-------------------------------------------------------------+
| Layer 1: HTTP API Dependency Layer                          |
| - Authenticates session token                               |
| - Validates caller has access to target restaurant_id       |
| - Rejects cross-tenant URL manipulation (403 Forbidden)      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Layer 2: Repository & ORM Query Scope                        |
| - BaseRepository automatically injects 'WHERE restaurant_id'|
| - Bulk operations enforce tenant ID in filter criteria      |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Layer 3: PostgreSQL Row-Level Security (RLS)                |
| - Database connection sets 'app.current_restaurant_id'      |
| - PostgreSQL kernel denies rows where restaurant_id != app  |
+-------------------------------------------------------------+
```

---

## 2. Row-Level Security (RLS) Policy Definitions

```sql
-- Enable RLS on all tenant-owned tables
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE menus ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE item_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE addons ENABLE ROW LEVEL SECURITY;
ALTER TABLE item_addons ENABLE ROW LEVEL SECURITY;
ALTER TABLE restaurant_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE restaurant_design_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Define tenant isolation policy for menus
CREATE POLICY tenant_isolation_policy_menus ON menus
    FOR ALL
    TO authenticated_app_user
    USING (restaurant_id = NULLIF(current_setting('app.current_restaurant_id', true), '')::uuid);

-- Define public menu read policy (Allow anonymous reading ONLY for published snapshots)
CREATE POLICY public_read_published_snapshots ON menu_versions
    FOR SELECT
    TO public_guest_user
    USING (
        id IN (SELECT active_version_id FROM publications WHERE publications.restaurant_id = menu_versions.restaurant_id)
    );
```

---

## 3. Mandatory Security Verification Test Matrix

These 8 security test cases must pass on CI/CD before any code merges to `main`:

| Test ID | Test Scenario | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| **SEC-01** | User A from Restaurant 1 attempts `GET /api/v1/restaurants/{id2}/menus` | HTTP 403 Forbidden | Automated (Pytest) |
| **SEC-02** | User A attempts `PATCH /api/v1/items/{item_id_from_rest_2}` with updated price | HTTP 404 Not Found / 403 Forbidden | Automated (Pytest) |
| **SEC-03** | User A attempts `POST /api/v1/restaurants/{id2}/publish` | HTTP 403 Forbidden | Automated (Pytest) |
| **SEC-04** | Anonymous public user queries `/api/v1/restaurants/{id}/menus` (internal drafts) | HTTP 401 Unauthorized | Automated (Pytest) |
| **SEC-05** | Anonymous public user requests `/api/v1/public/restaurants/{slug}/menu` for unpublished menu | HTTP 404 Not Found | Automated (Pytest) |
| **SEC-06** | Manager with role `menu_editor` attempts `DELETE /restaurants/{id}` | HTTP 403 Forbidden (Requires `owner`) | Automated (Pytest) |
| **SEC-07** | SQL Injection payload injected into `restaurantSlug` parameter | Sanitized & Rejected (404/422) | Automated (Pytest) |
| **SEC-08** | Direct raw SQL query on `menu_items` with tenant context set to Restaurant 1 | Zero rows returned belonging to Restaurant 2 | Database RLS Test |
