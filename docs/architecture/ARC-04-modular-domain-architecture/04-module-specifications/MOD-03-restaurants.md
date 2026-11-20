# MOD-03 — Restaurant Management & Configuration Module Specification

**Module ID:** MOD-03  
**Tier:** Platform Foundation (P0)  
**Package:** `app.modules.restaurants`  

---

## 1. Ownership & Boundaries
- **Owns:** Restaurant profile, name, address, contact, slug, activation status, settings.
- **Does Not Own:** Menu catalog items, pricing rules, theme token storage.

## 2. Domain Model & Invariants
- **Restaurant Entity:** `Restaurant(id, organization_id, name, slug, is_active, settings)`
  - Restaurant must belong to an organization.
  - Slugs must be URL-safe (`RestaurantSlug`).
- **RestaurantSettings:** Validates currency (3-letter uppercase) and timezone.

## 3. Public Contracts & Events
- **Provides:** `RestaurantReader` Protocol (`restaurant_exists`, `is_restaurant_active`).
- **Consumes:** `OrganizationReader` Protocol.
- **Emits:** `RestaurantCreated` (EVT-004), `RestaurantDeactivated` (EVT-005).
