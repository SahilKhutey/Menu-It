# Publication Lifecycle Standard
**State Transitions & Activation Semantics**

## Lifecycle Overview
Draft edits stay strictly isolated in working storage.
When a publication transaction commits:
1. Frozen snapshot created with cryptographic SHA-256 digest.
2. Active pointer shifts transactionally.
3. Outbox worker broadcasts `MenuPublished` event.
4. Edge CDN and browser caches are invalidated.
