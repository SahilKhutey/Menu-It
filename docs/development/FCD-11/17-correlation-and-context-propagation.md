# FCD-11 · Document 17: Request Correlation, Trace Context Propagation & Causality Tracking

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Correlation Identifiers

Every interaction across the Menu-It platform carries three distinct identifiers:

1. **`request_id`:** Unique identifier generated per HTTP request by `RequestIDMiddleware` (UUID or client-supplied `X-Request-ID`), returned in response header `X-Request-ID`.
2. **`correlation_id`:** Cross-service causal chain identifier passed across HTTP calls, message queues, and async background jobs.
3. **`trace_id`:** 128-bit OpenTelemetry trace identifier linking all spans belonging to a single logical user transaction.

---

## 2. Asynchronous Context Propagation

When an event is dispatched to the background outbox or job queue:
1. The publisher captures `correlation_id`, `traceparent`, and `organization_id`.
2. These context properties are serialized into the job payload / outbox message headers.
3. When the ARQ worker or event dispatcher dequeues the message, it restores the correlation ID and resumes the OpenTelemetry span context, preserving complete causal lineage.
