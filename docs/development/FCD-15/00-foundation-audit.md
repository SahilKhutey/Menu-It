# FCD-15 — 00 Foundation & FCD-14 Audit

## Objective
Inspect existing FCD-01 through FCD-14 entities, services, storage, caching, audit, permissions, and frontend components before designing FCD-15 tables and services.

## Audit Findings

### 1. Existing Restaurant, Branch, and Settings Models (FCD-06 & FCD-14)
- **`restaurants` (`Restaurant`)**: Stores `organization_id`, `name`, `slug`, `description`, `email`, `phone`, `website`, `cuisine_type`, `timezone`, `status`. Has composite unique constraint `uq_restaurants_org_id` on `(organization_id, id)`.
- **`branches` (`Branch`)**: Stores `organization_id`, `restaurant_id`, `name`, `slug`, `branch_code`, `email`, `phone`, `address_line_1/2`, `city`, `state_region`, `postal_code`, `country_code`, `latitude`, `longitude`, `timezone`, `status`. Has composite FK `fk_branch_restaurant_tenant` and unique constraint `uq_branch_org_restaurant_id` on `(organization_id, restaurant_id, id)`.
- **`restaurant_profiles` (`RestaurantProfileRecord`)**: Created in FCD-06 with `public_name`, `legal_name`, `description`, `email`, `phone`, `address_*`, `primary_currency`, `timezone`, `schedule_payload`, `website_url`, `logo_asset_id`, `banner_asset_id`, `version`. FCD-15 can extend `restaurant_profiles` with `short_description`, `cuisine_type`, `price_range`, `public_email`, `public_phone`, and `social_links` rather than duplicating the table.
- **`organization_settings` & `restaurant_settings`**: Exist as JSONB payload tables from FCD-14.

### 2. Platform Infrastructure (FCD-05, FCD-09, FCD-10, FCD-11)
- **File Storage (`platform/files/application/service.py`)**: `FileService` already handles magic-byte MIME validation, tenant-scoped `build_storage_key`, `FileStorage` (`put`/`get`/`delete`), and `FileModel` metadata. FCD-15 branding uploads will wrap `FileService` directly.
- **Caching (`platform/cache/service.py`)**: `CacheService` provides `get_json`, `set_json`, `delete`, and `invalidate_organization_resource`.
- **Events & Audit (`platform/events/publisher.py`, `platform/audit/publisher.py`)**: `OutboxEventPublisher` and `OrganizationAuditEvent` / `SecurityAuditEventModel` are operational.
- **Permissions (`authorization/permissions.py`)**: Already includes `restaurant:read`, `restaurant:update`, `branch:read`, `branch:update`, `menu:publish`. FCD-15 will add granular configuration/publication permissions if needed or map cleanly to `restaurant:update` / `branch:update` / `restaurant:publish_profile`.

### 3. Domain Value Objects (FCD-06)
- `domain/value_objects/operating_hours.py` already provides `Weekday`, `DailyOperatingHours`, `WeeklyOperatingSchedule`, and `TimeRange` with `closes_next_day` overnight support and overlap detection.

### 4. Gap Register (What FCD-15 Must Add)
1. **Profile extensions**: `short_description`, `cuisine_type`, `price_range`, `public_email`, `public_phone`, `social_links` on `restaurant_profiles` (preserving backward compatibility with FCD-06).
2. **Branding**: `restaurant_branding` table + `HexColor` value object + `FileService` integration for logo/alternate logo/cover/favicon.
3. **Normalized Schedules & Exceptions**: `restaurant_weekly_hours`, `restaurant_schedule_exceptions`, `restaurant_schedule_exception_intervals`, `branch_weekly_hours`, `branch_schedule_exceptions`, `branch_schedule_exception_intervals`, plus IANA timezone + DST `is_open_now` evaluator with injected clock.
4. **Service Modes & Operational Settings**: `restaurant_service_configurations`, `restaurant_operational_settings`, `branch_configurations`, `branch_service_configurations` with explicit override presence (`None` = inherit, `False` = explicitly disabled, `True` = explicitly enabled).
5. **Configuration Resolver**: Pure deterministic `build_effective_configuration` + `RestaurantConfigurationResolver` service + `CacheService` invalidation.
6. **Public Profile & Publications**: `restaurant_publications` & `restaurant_configuration_revisions` with immutable revision snapshots, atomic publish/unpublish/restore, and strict public DTO allowlisting (`GET /api/v1/public/restaurants/{slug}`).
7. **Frontend**: Restaurant settings shell and editors in `apps/web/src/app/dashboard/restaurants/[restaurantId]/settings/*` and reusable components in `packages/ui` or feature components, backed by `@menu-it/shared-types`.
