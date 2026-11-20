# 16 — Alembic Migration Strategy

## 1. Migration Sequence

Migrations follow strict dependency order:
1. Extensions & global types
2. Identity (`users`, `user_sessions`)
3. Tenancy (`organizations`, `organization_members`)
4. Restaurants (`restaurants`, `restaurant_settings`)
5. Menus, Categories, Items
6. Pricing & Variants
7. Presentation & Design Configs
8. Menu Versions & Publications
9. Media & Licensing
10. Governance & RLS Policies
