# FCD-10 — Transactional Outbox Pattern & Dispatch Guarantees

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. The Dual-Write Problem & Solution

Writing business data to PostgreSQL and publishing an event to Redis in separate uncoordinated steps risks inconsistent states (e.g. order saved, but notification event lost due to Redis network failure).

The **Transactional Outbox Pattern** resolves this:
1. `OutboxEventPublisher.publish()` inserts a row into `event_outbox` in the same PostgreSQL transaction as the business operation.
2. The caller commits both entities atomically.
3. If the transaction rolls back, the outbox record is rolled back automatically.

---

## 2. Outbox Dispatcher

`OutboxDispatcher.process_batch()`:
- Queries unpublished rows: `WHERE published_at IS NULL AND (next_attempt_at IS NULL OR next_attempt_at <= NOW())`.
- Employs `FOR UPDATE SKIP LOCKED` in PostgreSQL for contention-free concurrent dispatch.
- Marks rows with `published_at = NOW()` upon successful delivery.
- On failure, reschedules with exponential backoff (`attempts += 1`, `next_attempt_at`).
