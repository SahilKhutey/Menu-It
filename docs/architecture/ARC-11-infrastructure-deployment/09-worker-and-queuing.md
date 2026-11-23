# 09 — Worker & Queuing Infrastructure
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Background Worker Architecture
The asynchronous worker (`backend/app/worker.py`) processes transactional outbox events, scheduled jobs, and media processing tasks without introducing heavy broker dependencies like RabbitMQ or Celery.

## 2. Key Operational Invariants
- **Tenant Context (ARC11-I10):** Every job execution envelope carries an authenticated `TenantJobContext(organization_id, actor_id)`.
- **Bounded Exponential Backoff:** Failed jobs retry with exponential backoff capped at 60 seconds (`min(base * 2^attempt, max_backoff)`).
- **Dead-Letter Queue (DLQ):** Jobs failing more than 5 times transition to `dead_letter` status with complete error tracebacks for manual inspection.
- **Graceful Shutdown:** Intercepts `SIGTERM`, finishes active in-flight jobs, and releases database locks cleanly.\n