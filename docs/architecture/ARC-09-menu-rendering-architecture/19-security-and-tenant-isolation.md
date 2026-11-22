# ARC-09 §19 — Security & Tenant Isolation

## 1. Multi-Tenant Isolation
The rendering pipeline enforces strict organizational tenant boundaries (ARC-05):
- Anonymous consumers can only access published snapshots keyed by `restaurant_slug` and `menu_slug`.
- Sibling tenant cross-lookup attempts return HTTP 404 (`ARC09-T119`).
- Internal database IDs (organization UUIDs, user IDs, Stripe customer IDs) are purged from public delivery payloads (`ARC09-T070`).

## 2. Injection Prevention
- **XSS Prevention**: Dish descriptions and titles are rendered exclusively as text nodes or sanitized content. Raw `<script>` tags are neutralized (`ARC09-T116`).
- **CSS Injection**: Theme token overrides are validated against strict hex color patterns (`#RRGGBB`) and approved font lists. Arbitrary CSS declarations cannot be injected (`ARC09-T117`).
