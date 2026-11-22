# ARC-10 §23: Observability & Telemetry
**Structured Logs, Metrics, and Operational Alerts**

## 1. Telemetry Metrics
- `publication_requests_total`
- `publication_success_total`
- `publication_failures_total`
- `publication_duration_seconds`
- `publication_rollback_total`
- `publication_outbox_pending_total`
- `publication_integrity_failures_total`

## 2. Structured JSON Logs
All lifecycle operations emit structured JSON logs with `operation_id`, `menu_id`, `actor_id`, and execution duration.
