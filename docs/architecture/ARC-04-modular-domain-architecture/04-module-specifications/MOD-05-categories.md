# MOD-05 — Category Management Module Specification

**Module ID:** MOD-05  
**Tier:** Core Business (P0)  
**Package:** `app.modules.categories`  

---

## 1. Ownership & Boundaries
- **Owns:** Category identity, name, display order, visibility.
- **Does Not Own:** Menu-level scheduling, food item recipes, pricing.

## 2. Domain Model & Invariants
- **Category Entity:** `Category(id, menu_id, name, display_order, is_visible)`
  - Deterministic ordering via non-negative `DisplayOrder`.
  - Visibility toggling without deleting content.

## 3. Public Contracts & Events
- **Provides:** `CategoryReader` Protocol (`category_exists`).
- **Consumes:** `MenuReader`.
- **Emits:** `CategoryCreated` (EVT-007).
