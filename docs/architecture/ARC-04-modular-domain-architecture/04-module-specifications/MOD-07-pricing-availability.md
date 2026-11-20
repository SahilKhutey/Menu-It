# MOD-07 — Pricing & Availability Module Specification

**Module ID:** MOD-07  
**Tier:** Core Business (P0)  
**Package:** `app.modules.pricing`  

---

## 1. Ownership & Boundaries
- **Owns:** Price records, currency, price validity, availability status.
- **Does Not Own:** Food item names, culinary descriptions, image assets.

## 2. Domain Model & Invariants
- **Price Entity:** `Price(id, item_id, amount, currency, is_active)`
  - Monetary values stored strictly as `Money` (finite non-negative `Decimal`).
  - Strict 3-letter currency code (e.g. `INR`).
- **AvailabilityRule Entity:** `AvailabilityRule(id, item_id, is_available, reason)`

## 3. Public Contracts & Events
- **Provides:** `PricingReader` Protocol (`get_item_price`).
- **Consumes:** `FoodItemReader`.
- **Emits:** `ItemPriceChanged` (EVT-009).
