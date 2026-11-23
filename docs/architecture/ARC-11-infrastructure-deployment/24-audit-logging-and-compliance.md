# 24 — Audit Logging & Compliance
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Audit Logging Standards
- Every administrative configuration change, role grant, tenant modification, and publishing action generates an immutable audit record.
- Structured JSON log format including: `timestamp`, `actor_id`, `organization_id`, `event_type`, `ip_address`, and `user_agent`.
- Logs forwarded to write-once append-only storage in compliance with SOC 2 / ISO 27001 requirements.\n