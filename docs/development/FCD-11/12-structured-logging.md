# FCD-11 · Document 12: Centralized Structured Logging Architecture

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Structured Logging Standard

In production, all backend components emit machine-readable JSON logs via `JsonFormatter` in `apps/api/src/menu_it/core/logging.py`:

```json
{
  "timestamp": "2026-11-26T09:25:00.123456Z",
  "level": "INFO",
  "logger": "menu_it.api.v1.restaurants",
  "message": "Restaurant profile updated successfully",
  "request_id": "req-98f24b2e",
  "correlation_id": "corr-a34f89d1",
  "organization_id": "org-6a4b1234-...",
  "user_id": "usr-8888-...",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "extra": {
    "restaurant_id": "rest-1234-...",
    "action": "profile_update"
  }
}
```

---

## 2. Context Injection Pipeline

1. **Request Ingress:** `RequestIDMiddleware` generates or captures `X-Request-ID` and sets context variables.
2. **Context Logger Adapter:** `get_context_logger(...)` binds request ID, correlation ID, tenant organization ID, and actor user ID.
3. **OpenTelemetry Integration:** `JsonFormatter` automatically queries `get_current_trace_and_span_id()` from OpenTelemetry to inject distributed trace and span IDs if active.
4. **Log Aggregation:** Logs sent to stdout are scraped by container log collectors (Fluentbit, Vector, or CloudWatch) and shipped to centralized Elasticsearch / Grafana Loki.
