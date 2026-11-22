# ARC-10 §14: Event & Outbox Architecture
**Transactional Outbox & Reliable Asynchronous Delivery**

## 1. Transactional Outbox Pattern
To prevent loss of events between PostgreSQL commit and message brokers or cache workers:
1. Publication events are inserted into `outbox_events` within the publication database transaction.
2. Background outbox worker claims unpublished events using `FOR UPDATE SKIP LOCKED`.
3. Worker dispatches events to registered consumers (cache invalidation, auditing).
4. On success, worker sets `published_at = NOW()`.
5. On failure, worker retries with bounded exponential backoff.
6. Repeated failures move event to dead-letter state for operator review.
