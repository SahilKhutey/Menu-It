# 08. Authorization and Permissions Architecture

## 1. Role-Based Permissions
Mapped in `backend/architecture/api_permissions.yaml`:
- `owner`: Full organizational control.
- `admin` / `org_admin`: Branch and menu management, member management.
- `manager`: Branch operations, menu editing, publishing.
- `editor`: Menu draft modifications, visual design.
- `viewer`: Read-only access to menu drafts and settings.

## 2. Fail-Closed Enforcement
The `require_permission` dependency validates fine-grained permissions against the server-derived `TenantContext`.
