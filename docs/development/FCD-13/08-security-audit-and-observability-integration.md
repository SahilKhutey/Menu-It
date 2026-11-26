# FCD-13 · Document 08 — Security, Audit & Observability Integration

## 1. Objective
Validates that FCD-11 security controls, append-only security audit logging, distributed tracing headers, and Prometheus telemetry metrics operate across the request and background processing lifecycles.

---

## 2. Integrated Observability Architecture

```
Incoming Request
  │
  ├──> RequestIDMiddleware (Enforces / generates valid UUID X-Request-ID)
  ├──> RequestTimingMiddleware (Calculates X-Response-Time-MS)
  ├──> SecurityHeadersMiddleware (HSTS, CSP, X-Content-Type-Options)
  ├──> LoggingMiddleware (Structured JSON log: timestamp, level, req_id, duration)
  │
  ▼
Execution & Domain Operations
  │
  ├──> RateLimiter (Token bucket rate limiting per IP / Tenant)
  ├──> AuditEventPublisher (Durable, append-only security audit record)
  └──> Prometheus Instrumentation (Counters, histograms, latency metrics)
```

---

## 3. Core Security & Observability Guarantees

1. **Structured Log Schema:**
   - Logs are output as structured JSON containing `timestamp`, `level`, `service`, `request_id`, `status_code`, and `duration_ms`.
   - Authorization headers, passwords, and API keys are scrubbed before logging.
2. **Prometheus Telemetry:**
   - Exposes application operational metrics at `GET /api/v1/metrics`.
   - Includes HTTP request durations, status code distributions, active database connections, and cache hit/miss counters.
3. **Audit Event Immutability:**
   - Security audit events are recorded to PostgreSQL `security_audit_events` with non-updatable append-only constraints.

---

## 4. Verification Matrix

| Test ID | Scenario | Expected Outcome | Verification Status |
| :--- | :--- | :--- | :---: |
| `OBSINT-T01` | Prometheus metrics scraping | `/api/v1/metrics` responds HTTP 200 with text/plain | **PASSED** |
| `OBSINT-T02` | Audit event logging | `LoggingAuditEventPublisher` dispatches valid audit event | **PASSED** |
| `OBSINT-T03` | Security headers | HSTS, X-Frame-Options, X-Content-Type-Options added | **PASSED** |
| `OBSINT-T04` | Secret redaction | Bearer tokens and passwords redacted in audit metadata | **PASSED** |
| `OBSINT-T05` | Request correlation | `X-Request-ID` and `X-Response-Time-MS` returned | **PASSED** |

---

## 5. Verification Evidence
Verified by: `apps/api/tests/integration/test_security_observability_integration.py` (all tests passing).
