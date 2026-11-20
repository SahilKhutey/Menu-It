# 02 — Data Ownership Model

## 1. Ownership Rules

The **Organization** is the authoritative primary tenant owner. A **Restaurant** is a subordinate operational branch resource.

- An organization owns its restaurants and custom themes.
- A restaurant owns its menus, categories, items, and branch settings.
- A menu owns its categories, items, and publication history.
- A menu publication references a specific immutable version snapshot.
- Media assets belong to an organization and associate with restaurants and food items.
- Users are global platform identities; access is mediated through organization memberships.

## 2. Ownership Scope Hierarchy

```
Global Platform Scope
  └── Organization Scope (organization_id)
        └── Restaurant Branch Scope (organization_id, restaurant_id)
              └── Menu Scope (organization_id, restaurant_id, menu_id)
```

Where a child record belongs to a restaurant, it also carries `organization_id`. This intentional denormalization enables composite foreign keys and PostgreSQL RLS to verify matching tenant ownership at every relational level.
