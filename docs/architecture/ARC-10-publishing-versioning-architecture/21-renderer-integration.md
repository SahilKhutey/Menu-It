# ARC-10 §21: Renderer Integration (ARC-09)
**Consuming Active Snapshots in Public Delivery**

## 1. Active Snapshot Resolution
Public guest requests to `/r/[slug]/[menuSlug]` query the authoritative active publication pointer:
1. Lookup active publication for menu.
2. Retrieve immutable snapshot payload.
3. Verify SHA-256 hash.
4. Pass directly to ARC-09 presentation composition engine.
5. Draft data is strictly unreachable.
