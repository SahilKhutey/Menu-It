# FCD-15 — 12 Platform Integration

All configuration mutations publish `EventEnvelope` records via `OutboxEventPublisher` (FCD-10), write `OrganizationAuditEvent` trails (FCD-09/FCD-11), and trigger `CacheService.invalidate_organization_resource(..., "restaurant_config")`.
