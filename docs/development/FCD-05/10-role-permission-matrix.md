# FCD-05 — Role-Permission Matrix

## 1. Organization Role Mapping

Organization roles govern platform access across all restaurants subordinate to the organization.

| Permission | OWNER | ADMIN | MANAGER | STAFF | VIEWER |
|---|:---:|:---:|:---:|:---:|:---:|
| `organization:read` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `organization:update` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `organization:manage_members` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `billing:read` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `billing:manage` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `restaurant:create` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `restaurant:read` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `restaurant:update` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `restaurant:archive` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `menu:read` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `menu:create` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `menu:update` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `menu:publish` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `order:read` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `order:create` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `order:update` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `order:cancel` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `staff:read` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `staff:invite` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `staff:update` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `staff:revoke` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `analytics:read` | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 2. Restaurant Branch Role Mapping

When a user is assigned to a specific branch restaurant, branch-level permissions govern restaurant operations if they hold no organization-level role.

| Permission | RESTAURANT_MANAGER | KITCHEN_STAFF | SERVICE_STAFF |
|---|:---:|:---:|:---:|
| `restaurant:read` | ✅ | ✅ | ✅ |
| `restaurant:update` | ✅ | ❌ | ❌ |
| `menu:read` | ✅ | ✅ | ✅ |
| `menu:update` | ✅ | ❌ | ❌ |
| `menu:publish` | ✅ | ❌ | ❌ |
| `order:read` | ✅ | ✅ | ✅ |
| `order:create` | ✅ | ❌ | ✅ |
| `order:update` | ✅ | ✅ | ✅ |
| `order:cancel` | ✅ | ❌ | ❌ |
| `staff:read` | ✅ | ❌ | ❌ |
| `staff:invite` | ✅ | ❌ | ❌ |
| `analytics:read` | ✅ | ❌ | ❌ |

---

## 3. Platform Administrative Roles

Platform roles are completely separated from tenant organizations and govern global SaaS operations.

| Permission | PLATFORM_ADMIN | PLATFORM_SUPPORT | PLATFORM_OPERATOR |
|---|:---:|:---:|:---:|
| `platform:manage_organizations` | ✅ | ❌ | ❌ |
| `platform:manage_users` | ✅ | ❌ | ❌ |
| `platform:manage_support_access`| ✅ | ✅ | ❌ |
| `platform:view_audit_logs` | ✅ | ✅ | ✅ |
