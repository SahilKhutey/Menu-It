# 04 — Entity-Relationship Diagrams

## 1. Core Relational Diagram

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ RESTAURANTS : owns
    ORGANIZATIONS ||--o{ ORGANIZATION_MEMBERS : has
    USERS ||--o{ ORGANIZATION_MEMBERS : joins
    RESTAURANTS ||--o{ MENUS : contains
    RESTAURANTS ||--o{ RESTAURANT_SETTINGS : configures
    MENUS ||--o{ MENU_CATEGORIES : groups
    MENU_CATEGORIES ||--o{ MENU_ITEMS : contains
    MENU_ITEMS ||--o{ ITEM_PRICES : priced_by
    MENU_ITEMS ||--o{ ITEM_VARIANTS : varies_by
    MENUS ||--o{ MENU_VERSIONS : snapshots
    MENUS ||--o{ PUBLICATIONS : published_as
    ORGANIZATIONS ||--o{ SUBSCRIPTIONS : subscribes
    ORGANIZATIONS ||--o{ AUDIT_LOGS : records
```

## 2. Composite Relational Links

Composite foreign keys enforce matching ownership across all tiers:
- `menus(organization_id, restaurant_id) -> restaurants(organization_id, id)`
- `menu_categories(organization_id, restaurant_id, menu_id) -> menus(organization_id, restaurant_id, id)`
- `menu_items(organization_id, restaurant_id, category_id) -> menu_categories(organization_id, restaurant_id, id)`
- `item_prices(organization_id, restaurant_id, item_id) -> menu_items(organization_id, restaurant_id, id)`
- `menu_versions(organization_id, restaurant_id, menu_id) -> menus(organization_id, restaurant_id, id)`
- `publications(organization_id, restaurant_id, menu_id, menu_version_id) -> menu_versions(organization_id, restaurant_id, menu_id, id)`
