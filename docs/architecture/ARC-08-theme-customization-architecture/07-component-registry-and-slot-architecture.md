# ARC-08 §7 — Component Registry & Slot Architecture

## 1. Registered Components (13 Platform Components)
1. `restaurant-header`: Brand logo, cover image, name, operational metadata. Slot: `header`.
2. `menu-title`: Title, subtitle, menu description, validity badge. Slot: `header`.
3. `category-navigation`: Sticky pills, tabs, or sidebar category jumps. Slot: `navigation`.
4. `category-heading`: Category title, description, badge, section divider. Slot: `category.header`.
5. `menu-item-card`: Primary menu item card with title, description, price, badges. Slot: `category.items`.
6. `menu-item-image`: High-res optimized WebP item photo with aspect ratio constraints. Slot: `category.items`.
7. `menu-item-price`: Multi-currency, fractional, variant, and portion pricing display. Slot: `category.items`.
8. `menu-item-description`: Rich text, allergen statement, preparation note. Slot: `category.items`.
9. `dietary-label`: Vegetarian, Vegan, Jain, Halal, Gluten-Free indicators. Slot: `category.items`.
10. `allergen-label`: Nuts, Dairy, Shellfish, Soy, Gluten compliance notices. Slot: `category.items`.
11. `availability-indicator`: Live sold-out badge, limited quantity tag. Slot: `category.items`.
12. `menu-footer`: Legal disclaimer, FSSAI compliance, tax notice, copyright. Slot: `footer`.
13. `contact-information`: Address, phone, social media, operating hours. Slot: `footer`.

## 2. Slot Governance
Components can only be assigned to their declared `supported_slots`. Placing a `menu-item-card` into `header` or `category-navigation` into `footer` is immediately rejected during schema validation with code `UNSUPPORTED_COMPONENT_SLOT`.
