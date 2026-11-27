# Devlog-029: FCD-15 Restaurant Profile, Branding & Operational Configuration Module

**Date:** 2026-11-27  
**Milestone / Tag:** `FCD-15`  
**Status:** Implemented & Verified  

---

## Summary
- **Pure Domain (`domain/restaurant_configuration/`)**: Implemented `HexColor`, `OpeningInterval` (overnight & multi-shift validation), `ScheduleExceptionEntry`, `evaluate_open_status` (IANA timezone + DST), `ServiceModeConfig`, `OperationalSettings`, and deterministic `build_effective_configuration` / `resolve_service_modes` (explicit `False` disables inheritance).
- **Database (`0010_fcd15_config`)**: Extended `restaurant_profiles` and added `restaurant_branding`, `restaurant_weekly_hours`, `restaurant_schedule_exceptions`, `restaurant_service_configurations`, `restaurant_operational_settings`, `branch_configurations`, `branch_weekly_hours`, `branch_service_configurations`, `restaurant_publications`, and `restaurant_configuration_revisions` with composite FKs and PostgreSQL RLS.
- **Services & API**: Added `RestaurantConfigurationService` and `RestaurantPublicationService` (optimistic concurrency, outbox events, audit logs, cache invalidation, immutable revision snapshots, allowlisted public endpoint `GET /api/v1/public/restaurants/{slug}`), bringing OpenAPI to 73 paths.
- **Frontend**: Added `packages/shared-types/src/restaurant-configuration.ts`, `apps/web/src/services/restaurant-config-api.ts`, and 8 App Router pages under `apps/web/src/app/dashboard/restaurants/[restaurantId]/settings/*`.
