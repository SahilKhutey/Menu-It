# 10 — SQLAlchemy 2.x Persistence Architecture

## 1. Declarative Base and Mixins

- `Base`: Declarative base with standardized PostgreSQL naming conventions.
- `UUIDPrimaryKey`: Mixin providing UUID primary key defaulting to `uuid4()`.
- `Timestamped`: Mixin providing UTC `created_at` and `updated_at`.
- `ImmutableTimestamped`: Mixin providing UTC `created_at` for immutable snapshots.
- `TenantScoped`: Mixin binding `organization_id`.
- `RestaurantScoped`: Mixin binding `organization_id` and `restaurant_id`.
