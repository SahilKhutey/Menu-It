# ARC-10 §10: Publication Transaction Architecture
**ACID Commit Boundaries & Row Locking**

## 1. Transaction Flow
1. Acquire menu row lock (`FOR UPDATE`).
2. Verify expected draft revision and active publication ID.
3. Validate candidate payload.
4. Insert `menu_publication_snapshots` record.
5. Insert `menu_publications` record with next version number.
6. Upsert `menu_active_publications` pointer.
7. Insert `publication_activations` ledger record.
8. Insert `outbox_events` transactional event (`MenuPublished`).
9. Commit database transaction.

## 2. Atomicity Guarantee
If any step fails, the entire transaction rolls back cleanly. Visitors continue seeing the previously active publication without disruption.
