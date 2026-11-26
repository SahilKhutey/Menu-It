# FCD-11 · Document 14: System Metrics, Business Telemetry & Prometheus Instrumentation

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Prometheus Telemetry Architecture

Platform telemetry is collected via `menu_it.platform.observability.metrics` and exposed to Prometheus via the `GET /api/v1/metrics` endpoint.

### Primary Metrics Catalog

| Metric Name | Type | Labels | Description |
| :--- | :--- | :--- | :--- |
| `http_requests_total` | Counter | `method`, `endpoint`, `status` | Total HTTP requests handled |
| `http_request_duration_seconds` | Histogram | `method`, `endpoint` | Latency distribution of HTTP requests |
| `database_connections_active` | Gauge | None | Number of active checked-out DB connections |
| `redis_operations_total` | Counter | `operation`, `status` | Redis commands executed (hit, miss, error) |
| `background_jobs_total` | Counter | `job_type`, `status` | Background jobs processed (completed, failed, retry) |
| `security_audit_events_total` | Counter | `event_type`, `outcome` | Security events recorded (success, denied, failure) |
| `rate_limit_exceeded_total` | Counter | `key_type` | Count of rate limit breaches triggered |

---

## 2. Scraping & Security

- **Endpoint:** `GET /api/v1/metrics` returns standard Prometheus text format (`text/plain; version=0.0.4`).
- **Access Control:** The metrics endpoint is accessible by internal infrastructure scrapers (Kubernetes service discovery) and protected from public client exposure.
