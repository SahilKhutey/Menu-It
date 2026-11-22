# ARC-09 §07 — Component Catalogue & Slot Resolution

## 1. Registered Component Catalogue
Only registered components from the ModularMenu catalogue may be rendered. Attempting to assign an unregistered component string to any layout slot causes a validation error (`RENDER_COMPONENT_NOT_FOUND`).

### Active Component Catalogue
- **Header Components**: `RestaurantHeroHeader`, `RestaurantMinimalHeader`, `RestaurantProfileHeader`
- **Navigation Components**: `CategoryPillNav`, `CategoryDropdownNav`, `CategorySidebarNav`
- **Section Components**: `CategorySection`, `CategoryTabSection`
- **Item Components**: `FoodItemCard`, `FoodItemListRow`, `FoodItemCompactRow`
- **Display Components**: `DietaryBadgeList`, `PriceDisplay`
- **Footer Components**: `MenuFooter`, `MenuLegalFooter`

## 2. Slot Fallback Hierarchy
If a restaurant's layout configuration fails to specify a slot or specifies a deprecated component, the resolver applies standard fallbacks:
- `header` -> `RestaurantHeroHeader`
- `navigation` -> `CategoryPillNav`
- `item_card` -> `FoodItemCard`
- `footer` -> `MenuFooter`
