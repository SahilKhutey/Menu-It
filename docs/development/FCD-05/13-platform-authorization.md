# FCD-05 — Platform Administrative Authorization & Privilege Separation

## 1. Separation of Tenant and Platform Privileges

A fundamental security failure in multi-tenant architectures occurs when tenant administrators or organization owners accidentally inherit platform-level privileges, or when platform operators can access tenant data without audit trails.

### Governing Invariant
> **Platform authority and tenant authority are mutually exclusive by default. Being an Organization Owner confers ZERO platform administrative capabilities, and being a Platform Admin confers ZERO tenant context without an explicit, audited assignment or support session.**

---

## 2. Platform Membership Entity

Platform authority is governed by a distinct table: `platform_memberships`.

| Column | Type | Description |
|---|---|---|
| `id` | `UUID` | Primary Key |
| `user_id` | `UUID` | Foreign Key (`users.id`, Unique) |
| `role` | `VARCHAR(32)` | Platform role (`platform_admin`, `platform_support`, `platform_operator`) |
| `status` | `VARCHAR(32)` | Lifecycle status (`active`, `suspended`, `revoked`) |
| `granted_by` | `UUID` | Foreign Key (`users.id`) of administrator who granted access |
| `created_at` | `TIMESTAMPTZ` | Timestamp of privilege grant |
| `updated_at` | `TIMESTAMPTZ` | Timestamp of last modification |

Implementation: [platform.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/database/models/platform.py)

---

## 3. Enforcement Dependency: `require_platform_role`

Endpoints designated for platform administrative operations gate access using `require_platform_role`:
```python
@router.get(
    "/platform/organizations",
    dependencies=[Depends(require_platform_role(PlatformRole.PLATFORM_ADMIN))],
)
async def list_all_saas_organizations(...) -> ...:
    ...
```
If the authenticated principal lacks an active record in `platform_memberships` with the required role, an HTTP 403 Forbidden is immediately raised.
