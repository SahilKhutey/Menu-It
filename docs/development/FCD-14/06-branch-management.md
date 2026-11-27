# FCD-14 — 06 Branch Management

## Service Implementation
`BranchManagementService` (`apps/api/src/menu_it/services/branch_management.py`) manages physical/operational locations under a restaurant.

## Key Operations
- **`create_branch`**: Validates `(organization_id, restaurant_id)` ownership, checks slug uniqueness within the restaurant, stores address, phone, geo-coordinates, and independent `timezone` (defaulting from restaurant/org if omitted), and emits `BranchCreated` via `OutboxEventPublisher`.
- **`list_branches` / `get_branch`**: Enforces both `organization_id` and `restaurant_id` scoping.
- **`update_branch`**: Updates location metadata, contact details, and timezone.
- **`transition_status`**: Uses `validate_branch_transition` (`domain/branch/lifecycle.py`) to transition between `draft`, `active`, `temporarily_closed`, and `archived`.
