# MOD-04 — Menu Management Module Specification

**Module ID:** MOD-04  
**Tier:** Core Business (P0)  
**Package:** `app.modules.menus`  

---

## 1. Ownership & Boundaries
- **Owns:** Menu identity, menu name, menu lifecycle, structural relationships.
- **Does Not Own:** Category ordering internals, dish descriptions, pricing values.

## 2. Domain Model & Invariants
- **Menu Entity:** `Menu(id, restaurant_id, name, status)`
  - Statuses: `DRAFT`, `ACTIVE`, `ARCHIVED`.
  - Non-empty name up to 255 characters.

## 3. Public Contracts & Events
- **Provides:** `MenuReader` Protocol (`menu_exists`).
- **Consumes:** `RestaurantReader`, `CategoryReader`.
- **Emits:** `MenuCreated` (EVT-006).
