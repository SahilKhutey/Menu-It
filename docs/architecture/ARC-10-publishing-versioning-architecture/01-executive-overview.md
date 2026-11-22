# ARC-10 §1: Executive Overview
**ModularMenu · Publishing & Versioning Architecture Series**

## 1. System Role & Purpose
ARC-10 establishes how restaurant menu changes move from editable working drafts into publicly accessible, immutable, versioned publications.
The publishing engine forms the controlled boundary between the restaurant's operational configuration and its public digital menu.

## 2. Core Guarantees
1. **Draft Isolation:** A draft is never publicly accessible before explicit publication.
2. **Snapshot Immutability:** Every successful publication creates an immutable snapshot with a canonical SHA-256 digest.
3. **Atomic Activation:** Visitors see either the previous complete menu or the new complete menu; partial publications are physically prevented via database transactions.
4. **Autonomous Payload:** A publication snapshot packages all required category, item, variant, theme, and layout configurations.
5. **Auditable Traceability:** Every publish and rollback action is immutably recorded with actor, reason, and timestamp.
6. **Non-destructive Rollback:** Rollback activates an earlier valid snapshot without rewriting historical records or altering version sequences.
7. **Concurrency & Idempotency:** Optimistic revision locks (`If-Match`) and menu-level row locks prevent conflicting publishes; idempotency keys prevent duplicate activations.
8. **Public Delivery Alignment:** ARC-09 public renderer consumes strictly the active published snapshot via high-performance cached endpoints.
