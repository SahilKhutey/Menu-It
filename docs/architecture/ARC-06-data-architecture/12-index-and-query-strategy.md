# 12 — Index and Query Strategy

## 1. Strategic Indexing

- `restaurants (organization_id, status)`
- `menus (organization_id, restaurant_id, status)`
- `menu_categories (organization_id, restaurant_id, menu_id, sort_order)`
- `menu_items (organization_id, restaurant_id, category_id, sort_order)`
- `item_prices (organization_id, restaurant_id, item_id)`

All list endpoints enforce server-side cursor pagination with bounded limits.
