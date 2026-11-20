# 10 — Database Ownership & Relational Constraints

## 1. The Cross-Tenant Foreign Key Vulnerability

If child tables only reference `parent_id` (e.g. `category.menu_id`), an attacker could attach a category in Organization A to a menu in Organization B.

## 2. Composite Foreign Keys

ModularMenu enforces composite foreign keys across all tenant hierarchies:

```sql
-- Menus table composite unique key
ALTER TABLE menus ADD CONSTRAINT uq_menus_tenant_id UNIQUE (organization_id, id);

-- Categories table composite foreign key
ALTER TABLE categories
ADD CONSTRAINT fk_categories_menus_composite
FOREIGN KEY (organization_id, menu_id)
REFERENCES menus (organization_id, id)
ON DELETE CASCADE;
```

This prevents database-level cross-tenant relationship creation.
