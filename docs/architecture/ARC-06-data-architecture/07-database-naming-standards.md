# 07 — Database Naming Standards

## 1. Conventions

| Object Type | Convention | Example |
|---|---|---|
| Tables | Plural snake_case | `menu_items`, `organizations` |
| Columns | Singular snake_case | `organization_id`, `created_at` |
| Primary Key | `pk_<table>` | `pk_menus` |
| Foreign Key | `fk_<table>_<columns>_<ref_table>` | `fk_menus_org_rest_restaurants` |
| Unique Constraint | `uq_<table>_<columns>` | `uq_restaurants_org_slug` |
| Check Constraint | `ck_<table>_<rule>` | `ck_item_prices_amount` |
| Indexes | `ix_<table>_<columns>` | `ix_menus_restaurant_status` |
