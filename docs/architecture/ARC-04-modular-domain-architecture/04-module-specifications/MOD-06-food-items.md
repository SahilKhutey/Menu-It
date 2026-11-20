# MOD-06 — Food Item Management Module Specification

**Module ID:** MOD-06  
**Tier:** Core Business (P0)  
**Package:** `app.modules.food_items`  

---

## 1. Ownership & Boundaries
- **Owns:** Food item identity, names, descriptions, dietary badges, allergens.
- **Does Not Own:** Currency, pricing arithmetic, tax computation.

## 2. Domain Model & Invariants
- **FoodItem Entity:** `FoodItem(id, category_id, name, description, status, dietary_labels, allergens)`
  - Statuses: `AVAILABLE`, `UNAVAILABLE`, `DEACTIVATED`.
  - Non-empty name; explicit dietary claims.

## 3. Public Contracts & Events
- **Provides:** `FoodItemReader` Protocol (`item_exists`).
- **Consumes:** `CategoryReader`, `MediaStorage`.
- **Emits:** `FoodItemCreated` (EVT-008).
