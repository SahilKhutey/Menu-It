# ARC-10 §12: Rollback Architecture
**Non-Destructive Historical Snapshot Reactivation**

## 1. Core Principle
Rollback activates an earlier immutable snapshot. It does not delete, edit, or overwrite version history.

## 2. Pre-Rollback Checks
- Target publication exists and belongs to the same menu and organization.
- Target snapshot content matches its cryptographic SHA-256 hash.
- Renderer contract is supported (e.g. contract `1.0`).
- Expected active publication ID matches caller's expectation.

## 3. Activation Flow
The active publication pointer is transactionally shifted to the target publication, an activation event is logged, and a `MenuRolledBack` outbox event is emitted.
