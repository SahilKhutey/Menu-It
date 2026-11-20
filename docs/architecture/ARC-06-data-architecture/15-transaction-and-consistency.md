# 15 — Transactions, Concurrency & Consistency

## 1. Optimistic Concurrency

Mutable entities enforce a `row_version` counter. Concurrent updates verify `row_version == :expected_version`, raising conflict errors on stale writes.

## 2. Outbox & Idempotency

- `outbox_events`: Transactionally captured events for reliable asynchronous processing.
- `idempotency_records`: Stores request hashes to prevent duplicate write side effects.
