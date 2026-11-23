# Monitoring & Telemetry Guide
**ModularMenu Operational Documentation**

## 1. Key Metrics & Endpoints
- `/health/live`: Process liveness (HTTP 200).
- `/health/ready`: Database and service readiness (HTTP 200).
- `/health/startup`: Initialization and preflight check.

## 2. Alert Thresholds
| Metric | Warning Threshold | Critical Threshold |
| :--- | :--- | :--- |
| API 5xx Error Rate | > 1% over 5m | > 5% over 2m |
| API p95 Latency | > 250 ms over 10m | > 1000 ms over 5m |
| Outbox Queue Lag | > 500 unprocessed | > 2000 unprocessed |
| Disk Free Space | < 20% available | < 10% available |
| TLS Certificate Expiry| < 30 days remaining | < 7 days remaining |\n