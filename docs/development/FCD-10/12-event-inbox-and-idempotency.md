# FCD-10 — Event Inbox & Consumer Idempotency

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Idempotent Consumer Pattern

Background workers operate under an **at-least-once** delivery model. Therefore, consumer handlers must be strictly idempotent.

---

## 2. The `processed_events` Inbox

The `EventInbox` class (`menu_it.platform.events.inbox`) manages consumer deduplication:
```sql
CREATE TABLE processed_events (
    consumer_name VARCHAR(150) NOT NULL,
    event_id UUID NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (consumer_name, event_id)
);
```
- `record_if_not_processed(consumer_name, event_id)` checks if `(consumer_name, event_id)` exists.
- If already present, the duplicate delivery is suppressed and logged.
- If absent, the record is inserted in the consumer's active database transaction.
