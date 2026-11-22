# ARC-10 §2: Scope & Requirements
**ModularMenu · Architecture Boundaries & Capability Priorities**

## 1. In Scope
- **Draft state:** Track editable changes and their revisions.
- **Validation:** Determine publication readiness across content, price, media, and design.
- **Snapshot creation:** Freeze content and presentation configuration.
- **Publication:** Atomically activate a validated snapshot.
- **Versioning:** Maintain immutable publication history.
- **Rollback:** Reactivate a previous publication without altering historical records.
- **Concurrency:** Prevent conflicting publication operations.
- **Scheduling (P1):** Support future publication activation.
- **Approval (P1):** Support optional publication approval policies.
- **Audit:** Record publishing actions and actors.
- **Events:** Deliver publication lifecycle events via transactional outbox.
- **Cache coordination:** Invalidate stale public content.
- **Public resolution:** Identify active publication for a menu.
- **Recovery:** Handle interrupted or failed publication workflows.

## 2. Out of Scope
- Visual editor canvas rendering (ARC-08).
- React HTML and CSS rendering engine (ARC-09).
- Database-wide entity relational schemas (ARC-06).
- User authentication and tenant identity resolution (ARC-05, ARC-07).
- Cloud CDN and edge infrastructure topology (ARC-11).
- Platform-wide disaster recovery and backup (ARC-12).
