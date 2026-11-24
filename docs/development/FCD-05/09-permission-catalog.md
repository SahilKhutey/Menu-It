# FCD-05 — Fine-Grained Permission Catalog

## 1. Permission Token Standards

All permissions in Menu-It follow the standardized format:
`<resource>:<action>`

Defined as a string enumeration (`Permission(StrEnum)`) in [permissions.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/authorization/permissions.py).

---

## 2. Catalog of Standard Platform & Tenant Permissions

| Resource Domain | Permission Token | Description |
|---|---|---|
| **Organization** | `organization:read` | View organization profile, metadata, and settings |
| | `organization:update` | Update organization settings, branding, and billing info |
| | `organization:manage_members` | Invite, modify, and revoke organization memberships |
| **Restaurant** | `restaurant:read` | View restaurant details and operating configurations |
| | `restaurant:create` | Provision a new restaurant under the organization |
| | `restaurant:update` | Modify restaurant operating hours, address, and settings |
| | `restaurant:archive` | Deactivate or archive a restaurant location |
| **Menu** | `menu:read` | Inspect menu categories, items, modifiers, and pricing |
| | `menu:create` | Draft new menus, sections, and catalog items |
| | `menu:update` | Edit existing menu items, prices, and allergen tags |
| | `menu:publish` | Publish menu versions to customer-facing channels |
| **Order** | `order:read` | View active orders, kitchen tickets, and historical orders |
| | `order:create` | Place new customer or POS orders |
| | `order:update` | Update order preparation status (preparing, ready, served) |
| | `order:cancel` | Cancel an order and process refunds |
| **Staff** | `staff:read` | View restaurant staff assignments and roster |
| | `staff:invite` | Invite staff members to a restaurant branch |
| | `staff:update` | Update staff shift roles and permissions |
| | `staff:revoke` | Revoke staff access to a restaurant |
| **Billing** | `billing:read` | View subscription tier, invoices, and payment receipts |
| | `billing:manage` | Upgrade/downgrade subscription and change payment methods |
| **Analytics** | `analytics:read` | Access sales reporting, operational metrics, and analytics |
| **Platform** | `platform:manage_organizations` | Administrative control over SaaS tenant organizations |
| | `platform:manage_users` | Platform-level user management and account suspension |
| | `platform:manage_support_access`| Grant purpose-limited audited support sessions |
| | `platform:view_audit_logs` | Inspect system-wide security audit and compliance logs |
