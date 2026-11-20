# 08 — Tenant Data Integrity Architecture

## 1. Cross-Tenant Relationship Prevention

In single-foreign-key architectures, an attacker might attach a category belonging to Tenant A to a menu belonging to Tenant B.

ModularMenu prevents this via composite foreign keys:
```sql
ALTER TABLE menu_categories
ADD CONSTRAINT fk_categories_menu
FOREIGN KEY (organization_id, restaurant_id, menu_id)
REFERENCES menus (organization_id, restaurant_id, id)
ON DELETE CASCADE;
```

This guarantees that the database engine rejects any cross-tenant attachment attempt with zero reliance on application code.
