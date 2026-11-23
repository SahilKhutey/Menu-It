# 19 — Performance & Benchmarking Standards
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Performance Service Level Objectives (SLOs)
- **API Read Latency:** p95 < 100 ms, p99 < 250 ms.
- **API Write Latency:** p95 < 200 ms, p99 < 500 ms.
- **Database Query Latency:** p95 < 50 ms for OLTP operations.
- **Public Menu SSR First Contentful Paint:** < 1.2 seconds.
- **Frontend JavaScript First Load Budget:** Strictly < 120 kB gzip compressed.
- **Worker Outbox Dispatch Throughput:** >= 500 events/second per worker process.\n