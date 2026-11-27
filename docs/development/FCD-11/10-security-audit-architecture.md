# FCD-11 · Document 10: Security Audit Logging & Forensics Architecture

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Security Audit Architecture

Security audit logging in Menu-It is distinct from application operational logging. It provides an append-only, tamper-resistant evidentiary record of all security-significant events:

### Core Capabilities
- **Dedicated Storage Table:** `security_audit_events` in PostgreSQL with migration `0008_security_audit_events`.
- **Database RLS:** Tenant isolation policy ensures tenants only read audit events for their own organization, while platform security operations can review cross-tenant forensic data.
- **Fail-Safe Persistence:** `SecurityAuditWriter` persists events to PostgreSQL. If the database transaction fails or is unavailable, the writer emits a high-priority structured log message to ensure the audit entry is never silently dropped.
- **Automatic Metadata Redaction:** Sensitive credentials (passwords, tokens, keys) in event metadata are scrubbed via `redact_mapping` before serialization.

---

## 2. Event Types & Taxonomy

| Event Category | Example Event Types | Logged Metadata |
| :--- | :--- | :--- |
| **Authentication** | `auth.login.success`, `auth.login.failed`, `auth.lockout`, `auth.password.changed` | IP address, user agent, actor ID, failure reason code |
| **Authorization** | `authz.permission_denied`, `authz.role_assigned`, `authz.role_revoked` | Required permission, assigned roles, target resource |
| **Tenant Boundary**| `tenant.boundary_breach_attempt`, `tenant.context_mismatch` | Context org ID, target resource org ID, request path |
| **Session Control** | `session.created`, `session.revoked`, `session.expired` | Session ID, device user agent, IP address |
| **System & Security** | `config.security_violation`, `ratelimit.exceeded`, `dlq.job_replayed` | Rate limit key, configuration key, job ID |
