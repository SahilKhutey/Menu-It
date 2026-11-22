# ARC-10 §4: Publishing Domain Architecture
**Modular Entities, Value Objects, and Relational Schema**

## 1. Domain Entities
- **MenuDraft:** Current editable working state for a menu.
- **DraftRevision:** Immutable historical snapshot of a draft edit, with monotonic revision number and parent reference.
- **Publication:** Immutable publication metadata record (id, organization_id, menu_id, version_number, snapshot_id, snapshot_hash, status).
- **PublicationSnapshot:** Frozen menu content and presentation configuration payload stamped with canonical SHA-256 hash.
- **ActivePublication:** Single authoritative pointer per menu selecting the active publication for public delivery.
- **PublicationActivation:** Historical ledger recording every activation and rollback event.
- **PublicationOperation:** Idempotency tracking record for in-flight and completed publishing workflows.
- **PublicationValidationRecord:** Audit trail of validation outcome, errors, and warnings for a draft revision.
- **ScheduledPublication:** Scheduled activation request for future execution.
- **PublicationEvent / OutboxEvent:** Durable lifecycle event for downstream cache invalidation and indexing.

## 2. Entity Diagram
```
ORGANIZATION ──< RESTAURANT ──< MENU ──< MENU_DRAFT ──< DRAFT_REVISION
                                  │
                                  ├──< PUBLICATION ──< PUBLICATION_SNAPSHOT
                                  ├──< ACTIVE_PUBLICATION (1:1 pointer)
                                  ├──< PUBLICATION_ACTIVATION (ledger)
                                  └──< PUBLICATION_OPERATION (idempotency)
```
