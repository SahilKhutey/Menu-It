# FCD15-ADR-009: FCD-10 Cache Invalidation for Restaurant Configuration

- **Status**: Accepted
- **Decision**: Reuse `CacheService.invalidate_organization_resource(organization_id, "restaurant_config")` on every configuration and publication mutation rather than building a separate cache layer.
