# Devlog 020 — FCD-06 Domain Models & Shared Business Foundation

**Date:** 2026-11-24  
**Author:** AI Architecture & Core Engineering Team  
**Subject:** Implementation, Verification, and Release of FCD-06 Domain Models & Shared Business Foundation  
**Milestone:** `v1.0.0-fcd06`  
**Phase:** Foundational Core Development (FCD-06)  
**Parent Documents:** FCD-01 through FCD-05, ARC-01 through ARC-12  

---

## 1. Objectives & Context

Phase **FCD-06** establishes the ubiquitous domain language, pure domain entities, business invariants, value objects, domain events, repository ports, and shared contracts (`@menu-it/shared-types` and backend DTOs) that all subsequent Menu-It business modules will safely build upon without duplicating foundational rules.

The core architectural achievements delivered in this phase include:
1. **Zero-Dependency Domain Core (`menu_it.domain`):** Pure Python domain models with **zero imports** from `fastapi`, `sqlalchemy`, or `pydantic`.
2. **Domain Base Primitives:** `Entity[T]`, `AggregateRoot` with uncommitted event recording/collection, and a dedicated `DomainError` exception hierarchy.
3. **Core Domain Value Objects:**
   - `Currency`: Supported registry (USD, EUR, GBP, CAD, AUD, JPY, INR, CHF, SGD, AED) with minor unit precision.
   - `Money`: Exact Decimal arithmetic, strictly rejecting floating-point types and enforcing currency matching.
   - `Percentage` & `TaxRate`: Precision Decimal percentages and tax calculation.
   - `EmailAddress` & `PhoneNumber`: Normalized RFC email and Google `phonenumbers` E.164 parsing.
   - `Slug` & `Address`: Kebab-case URL slug and physical address validation.
   - `TimeZone`: Authoritative IANA validation via `zoneinfo.ZoneInfo`.
4. **Operating Schedule Foundation:**
   - `TimeRange`: Half-open `[opens_at, closes_at)` interval supporting late-night shifts crossing midnight with timeline intersection overlap logic.
   - `DailyOperatingHours`: Single-weekday schedule preventing overlapping shifts and closed-day range assignments.
   - `WeeklyOperatingSchedule`: Full 7-day schedule ensuring unique weekdays (Monday through Sunday) with convenience queries (`is_open_at`, `is_open_on`).
5. **Restaurant Business Profile Aggregate Root (`RestaurantProfile`):**
   - Explicit mutation methods advancing optimistic locking version counters and emitting domain events (`RestaurantProfileUpdated`, `RestaurantOperatingHoursUpdated`).
   - Lifecycle state transitions (`RestaurantLifecycleState`) verifying permitted operational state changes.
   - Multi-tenant ownership invariant (`assert_restaurant_belongs_to_organization`).
6. **Inverted Repository & Unit of Work Ports (`menu_it.domain.ports`):**
   - Structural `typing.Protocol` interfaces for `RestaurantProfileRepository`, `MenuItUnitOfWork`, and `DomainEventPublisher`.
7. **Shared API Transport & TypeScript Contracts:**
   - Standardized Pydantic schemas in `menu_it.contracts` (`APIResponse`, `ResponseMetadata`, `APIError`, `PaginationMeta`, `RestaurantProfileResponse`).
   - Synchronized TypeScript contracts in `packages/shared-types` (`common.ts`, `organization.ts`, `restaurant.ts`).
8. **Relational Persistence & PostgreSQL Row-Level Security:**
   - `RestaurantProfileRecord` SQLAlchemy model with composite foreign key constraint `(organization_id, restaurant_id) -> restaurants(organization_id, id)`.
   - Domain-to-persistence mapper (`RestaurantProfileMapper`).
   - Repository adapter (`SQLAlchemyRestaurantProfileRepository`) with optimistic concurrency conflict detection.
   - Alembic migration `0004_restaurant_profiles` with PostgreSQL RLS policy `restaurant_profiles_tenant_isolation`.
9. **Full Automated Verification:**
   - 219 automated unit, contract, and integration tests passing 100%.
   - 92% overall backend codebase coverage (100% on domain core).
   - 21 comprehensive technical documents in `docs/development/FCD-06/`.

---

## 2. Key Engineering Accomplishments

### 2.1 Domain Layer Implementation
- `apps/api/src/menu_it/domain/base/`: `Entity[T]`, `AggregateRoot`, `DomainEvent`, and `DomainError` hierarchy.
- `apps/api/src/menu_it/domain/shared/`: Strongly-typed identifiers (`OrganizationId`, `RestaurantId`, `UserId`).
- `apps/api/src/menu_it/domain/value_objects/`: `Currency`, `Money`, `Percentage`, `TaxRate`, `EmailAddress`, `PhoneNumber`, `Slug`, `Address`, `TimeZone`, `TimeRange`, `DailyOperatingHours`, `WeeklyOperatingSchedule`.
- `apps/api/src/menu_it/domain/organization/`: `OrganizationReference`.
- `apps/api/src/menu_it/domain/restaurant/`: `RestaurantReference`, `RestaurantProfile`, `RestaurantLifecycleState`, `assert_restaurant_belongs_to_organization`, and domain events (`RestaurantProfileUpdated`, `RestaurantStatusChanged`, `RestaurantOperatingHoursUpdated`).

### 2.2 Shared Contracts
- `apps/api/src/menu_it/contracts/`: `common.py`, `errors.py`, `pagination.py`, `organization.py`, `restaurant.py`.
- `packages/shared-types/src/`: `common.ts`, `organization.ts`, `restaurant.ts`, `index.ts`.

### 2.3 Persistence & Infrastructure Adapters
- `apps/api/src/menu_it/database/models/restaurant_profile.py`: `RestaurantProfileRecord` with composite FK `fk_restaurant_profiles_org_restaurant`.
- `apps/api/src/menu_it/infrastructure/mappers/restaurant_profile_mapper.py`: `RestaurantProfileMapper`.
- `apps/api/src/menu_it/infrastructure/repositories/restaurant_profile_repository.py`: `SQLAlchemyRestaurantProfileRepository`.
- `apps/api/src/menu_it/services/restaurant_profile.py`: `UpdateRestaurantProfileService` and `UpdateRestaurantProfileCommand`.
- `apps/api/alembic/versions/0004_create_restaurant_profiles.py`: Alembic revision `0004_restaurant_profiles`.

---

## 3. Verification & Metrics

- **Unit Tests:** 56 tests passing in 0.56s.
- **Contract Tests:** 9 tests passing in 0.32s.
- **Integration Tests:** 154 tests passing including migration lifecycle `0001 -> 0004 -> 0003 -> 0002 -> 0001 -> base -> 0004`.
- **Total Suite:** 219 tests passing (100% success rate).
- **Code Coverage:** 92% across entire backend application.
- **Static Analysis:** Ruff checks clean, Prettier format clean, TypeScript typecheck clean across all workspaces.
