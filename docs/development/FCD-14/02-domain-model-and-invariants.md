# FCD-14 — 02 Domain Model & Invariants

## Pure Domain Layer
All domain entities and invariants live under `apps/api/src/menu_it/domain/` with zero infrastructure imports (`fastapi`, `sqlalchemy`, `redis`, `httpx`, `menu_it.database`), verified by `apps/api/tests/integration/test_architecture_boundaries.py`.

## Entities & Value Rules
- **`OrganizationEntity` & `OrganizationSettingsEntity`** (`domain/organization/entities.py`): Enforces valid ISO 3166-1 alpha-2 `country_code` (`validate_country_code`), non-empty names/slugs, and valid currency/timezone defaults.
- **`RestaurantEntity` & `RestaurantSettingsEntity`** (`domain/restaurant/entities.py`): Enforces organization ownership, unique slug within organization, and restaurant-specific operational configuration.
- **`BranchEntity` & `BranchLifecycleState`** (`domain/branch/{entities.py,lifecycle.py}`): Models physical branches with `validate_branch_transition` enforcing valid state transitions across `draft`, `active`, `temporarily_closed`, and `archived`.
- **`OrganizationMembershipEntity`, `RestaurantMembershipEntity`, `BranchAssignmentEntity`** (`domain/membership/{entities.py,policies.py}`):
  - `ensure_not_removing_final_owner`: Raises `BusinessRuleViolationError` if removing or demoting an active owner would leave the organization with zero active owners.
  - `ensure_same_organization_scope`: Prevents cross-organization membership or branch assignment leakage.
- **`OrganizationInvitationEntity` & `InvitationStatus`** (`domain/invitation/{entities.py,lifecycle.py}`):
  - `ensure_invitation_acceptable`: Rejects expired, revoked, or already-accepted invitations and validates case-insensitive actor email matching.
