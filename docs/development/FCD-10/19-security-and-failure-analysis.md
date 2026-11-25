# FCD-10 — Security & Failure Mode Analysis

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Threat Modeling & Mitigation

| Threat | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Cross-Tenant Worker Context Leakage** | Critical | Fresh database sessions per task; transaction-local `set_config('app.current_organization_id', true)`. |
| **Arbitrary Code Execution via Payloads** | Critical | Strict registry `JOB_REGISTRY`. API callers can only invoke permitted registered string job types. |
| **Cache Poisoning / Cross-Tenant Collision**| High | Server-resolved `organization_id` embedded in keys: `menu-it:v1:org:{org_id}:...`. |
| **Sensitive Credential Leakage in DLQ** | High | Passwords and tokens scrubbed prior to persistence via `redact_mapping`. |

---

## 2. Failure Recovery Modes

1. **Redis Down:** Outbox events remain durable in PostgreSQL until Redis recovers.
2. **Worker Crash:** ARQ unacknowledged jobs are reclaimed upon worker restart.
3. **Consumer Error:** Failed events are retried with exponential backoff up to max attempts.
