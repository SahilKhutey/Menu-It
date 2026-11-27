# FCD-14 — 05 Restaurant Management

## Service Implementation
`RestaurantManagementService` (`apps/api/src/menu_it/services/restaurant_management.py`) handles restaurant brands inside an organization.

## Key Operations
- **`create_restaurant`**: Enforces unique `(organization_id, slug)`, creates `Restaurant` and `RestaurantSettings`, and publishes `RestaurantCreated` to the transactional outbox.
- **`list_restaurants` / `get_restaurant`**: Strictly scoped by `organization_id` to prevent cross-tenant reads (`EntityNotFoundError` when `restaurant_id` does not belong to `organization_id`).
- **`update_restaurant` / `update_settings`**: Updates profile/contact details or regional settings and emits audit + outbox events.
- **`transition_status`**: Delegates to FCD-04 `transition_restaurant` lifecycle engine (`draft`, `active`, `suspended`, `archived`).
- **`list_members` / `assign_member`**: Assigns organization members to restaurant-level roles (`RestaurantMembership`) after validating same-organization membership.
