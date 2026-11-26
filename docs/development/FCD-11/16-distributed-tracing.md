# FCD-11 · Document 16: Distributed Tracing & OpenTelemetry Integration

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Distributed Tracing Architecture

Menu-It integrates OpenTelemetry (`opentelemetry-api` and `opentelemetry-sdk`) to provide end-to-end visibility across distributed workflows:

- **Tracer Provider:** Configured in `menu_it.platform.observability.tracing` via `configure_tracing()`.
- **W3C Standard Context:** Trace IDs and Span IDs follow W3C Trace Context specifications (`traceparent` header).
- **Context Extraction & Injection:**
  - Inbound HTTP requests extract trace context via `extract_trace_context(headers)`.
  - Outgoing external requests and asynchronous background jobs inject trace context via `inject_trace_context(headers)`.
- **Correlation:** Active trace IDs and span IDs are automatically extracted via `get_current_trace_and_span_id()` and embedded into JSON log records and error envelopes.

---

## 2. Span Hierarchy Example

```
[HTTP Request: POST /api/v1/restaurants/{id}/menu-items]
 ├── [Authentication & Token Verification]
 ├── [TenantContext Resolution]
 ├── [DB: Transaction Begin & set_database_tenant_context]
 ├── [Service: CreateMenuItem]
 │    ├── [Validation & Image Upload]
 │    └── [DB: Insert menu_items]
 ├── [Event Outbox: Publish MenuItemCreated]
 └── [DB: Commit Transaction]
```
