# 05 — Logical Data Model

## 1. Domain Entities & Value Objects

- **Money:** Handled via integer minor units (`amount_minor` BIGINT) or fixed-scale `NUMERIC(12,2)`. Floating point types are prohibited.
- **Identifiers:** All entities utilize universally unique identifiers (UUIDv4) represented natively or via platform-independent GUID types.
- **Timestamps:** All temporal attributes enforce `TIMESTAMPTZ` stored in UTC.
- **Slugs:** Normalized lowercase kebab-case strings constrained for uniqueness at appropriate scopes.
