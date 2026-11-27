# FCD-07 §16 — Performance Benchmarks & Telemetry Standards

## 1. Request Performance Objectives

Menu-It enforces strict latency budgets for standard API requests:
- **Health Probes (`/api/v1/health/*`):** < 5 ms.
- **Read Requests (Cached or Indexed Queries):** < 50 ms.
- **Write Requests (Transactional Insert with RLS):** < 150 ms.

---

## 2. In-Flight Timing Telemetry

Every request executed through the FastAPI pipeline is timed by `RequestTimingMiddleware`:
- Injects header `X-Response-Time-MS: <float>`.
- Client and front-office monitoring services can inspect execution duration without adding client-side measuring overhead.

---

## 3. Structured Telemetry & Access Logging

`RequestLoggingMiddleware` emits structured log events formatted for ingestion into log aggregation tools (e.g. Datadog, CloudWatch, Loki):
- Fields: `timestamp`, `level`, `logger`, `method`, `path`, `status_code`, `request_id`, `duration_ms`.
- Header sanitization ensures GDPR and PCI-DSS compliance by preventing token or cookie serialization.
