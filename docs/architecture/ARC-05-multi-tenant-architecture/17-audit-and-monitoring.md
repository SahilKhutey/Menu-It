# 17 — Audit Logging & Security Monitoring

## 1. Audited Security Events

- `CROSS_TENANT_ACCESS_ATTEMPT`: Unauthorized access attempt to a foreign organization or branch.
- `MEMBERSHIP_ROLE_CHANGED`: Membership promotion or demotion.
- `MENU_PUBLISHED` / `MENU_ROLLED_BACK`: Atomic production changes.
- `SUPPORT_SESSION_INITIATED`: Time-bounded support operator access.

## 2. PII & Secret Redaction

Audit log payloads are filtered through redaction rules to guarantee that passwords, API tokens, and sensitive diner telemetry are never written to disk.
