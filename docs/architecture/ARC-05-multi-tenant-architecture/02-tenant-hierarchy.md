# 02 — Tenant Hierarchy & Structural Scopes

## 1. Tenancy Hierarchy

```
[ Global Platform Realm ]
           │
           ▼
[ Organization (Primary Tenant) ]
   ├── Memberships (Users + Roles)
   ├── Subscriptions & Entitlements
   ├── Custom Themes
   └── Restaurants (Branches)
          ├── Restaurant Settings
          ├── Menus
          │     ├── Categories
          │     └── Food Items
          │           ├── Pricing Rules
          │           └── Portion Availabilities
          ├── Editor Drafts (Private)
          ├── Published Snapshots (Public read)
          └── Media Assets
```

## 2. Scope Definitions

1. **Global Identity Scope:** User accounts (`users`) are global platform entities. A user may hold memberships across multiple independent organizations.
2. **Primary Tenant Scope (`organization_id`):** The legal and administrative customer boundary. All billing, data ownership, themes, and branches belong to an organization.
3. **Subordinate Branch Scope (`restaurant_id`):** An operating branch belonging to an organization. Users may have organization-wide branch access (owners/admins) or explicitly restricted branch access (managers/editors).
4. **Menu Scope (`menu_id`):** Menus and hierarchical categories/items subordinate to a restaurant branch.
