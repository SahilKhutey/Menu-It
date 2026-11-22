# ARC-10 §25: Testing Strategy
**Acceptance Testing Hierarchy & Test Levels**

## 1. Multi-Level Testing
- **Domain Unit Tests:** State machines, canonical hashing, revision increments.
- **Validation Engine Tests:** Rule enforcement, diagnostics formatting, allowlist filtering.
- **Database Integration Tests:** PostgreSQL constraints, row locks, transaction rollbacks.
- **Concurrency Tests:** Race conditions, duplicate idempotency keys, simultaneous publishes.
- **Outbox Worker Tests:** Event claiming, retry policy, dead letter handling.
- **API Tests:** Endpoints, HTTP status codes, RFC 9457 problem details.
- **Frontend Tests:** Component rendering, dialogs, build verification.
