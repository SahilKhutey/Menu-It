# 12 — Tenant Cache Isolation Architecture

## 1. Namespace Convention

Every cache key must be tenant-prefixed:
`tenant:{organization_id}:restaurant:{restaurant_id}:{resource}:{id}`

## 2. Cache Invalidation Triggers

- **Membership Revocation:** Immediately evicts cached authorization policies for the affected user and organization.
- **Menu Publication:** Invalidates previous publication cache entries and updates public edge cache headers.
- **Organization Switch:** Frontend query client evicts previous organization queries from local state.
