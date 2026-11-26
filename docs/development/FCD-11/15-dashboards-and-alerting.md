# FCD-11 · Document 15: Operational Dashboards, Alerting Rules & Threshold Engineering

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Operational Dashboard Hierarchy

The platform defines three standardized Grafana dashboards:

1. **Platform Executive Overview:** High-level availability, active tenant count, orders per minute, gross transaction volume, aggregate error budget burn rate.
2. **API & Service Health:** HTTP request rates, p95/p99 latency percentiles by route, 5xx server error ratios, rate limit violations, database query durations.
3. **Infrastructure & Workers:** Database pool saturation, Redis memory and command rates, ARQ job queue depths, dead-letter rates, host CPU and memory consumption.

---

## 2. Alerting Rules & Severity Tiers

| Severity | Alert Condition | Notification Channel | Target Response Time (MTTA) |
| :--- | :--- | :--- | :--- |
| **P1 — Critical** | Service availability < 99.0% over 5m; DB pool 100% saturated; DLQ spike > 50 jobs | PagerDuty / On-Call Phone | < 5 minutes |
| **P2 — High** | Error rate > 1.0% over 10m; p99 latency > 2.0s; Redis connectivity failures | Slack #incidents / PagerDuty | < 15 minutes |
| **P3 — Warning** | Rate limit breaches > 100/min; background job retries elevated; disk usage > 80% | Slack #platform-alerts | < 4 hours |
| **P4 — Info** | Routine certificate renewal; maintenance window events | Slack #platform-feed | Next business day |
