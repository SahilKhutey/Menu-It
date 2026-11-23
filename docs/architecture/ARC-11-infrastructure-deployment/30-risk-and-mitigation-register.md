# 30 — Risk & Mitigation Register
**ARC-11: Infrastructure & Deployment Architecture**

## Operational Risk Analysis (R-01 – R-12)
| Risk ID | Description | Impact | Probability | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **R-01** | Database migration locks active tables | High | Low | Enforce expand-and-contract pattern; ban table locks in migrations. |
| **R-02** | Redis cache cluster failure | Medium | Low | Architectural graceful degradation (ARC11-I03); bypass cache seamlessly. |
| **R-03** | Outbox worker backlog accumulation | Medium | Medium | Automated lag telemetry, bounded backoff, DLQ dead-letter routing. |
| **R-04** | Accidental credential exposure in logs | Critical | Low | Pydantic secret masking, strict regex sanitizer in logger. |
| **R-05** | Local storage directory traversal escape | Critical | Low | Strict canonical path normalization in LocalStorageAdapter. |
| **R-06** | Disk exhaustion from unrotated logs | High | Medium | Docker json-file log rotation (`max-size: 50m`, `max-file: 5`). |
| **R-07** | SSL/TLS certificate silent expiration | High | Low | Automated 30-day expiry alerting in monitoring guide. |
| **R-08** | Container privilege escalation | High | Low | `no-new-privileges: true`, non-root users, `cap_drop: [ALL]`. |
| **R-09** | Database restore failure during disaster | Critical | Low | Scheduled semi-annual automated restore drills. |
| **R-10** | Frontend bundle size bloat (> 120 kB) | Medium | Medium | Standalone Next.js build, bundle analyzer gate in CI pipeline. |
| **R-11** | Customer-hosted environment divergence | Medium | Low | Image compatibility manifest and preflight verification scripts. |
| **R-12** | Cross-tenant data leakage in jobs | Critical | Low | TenantJobContext envelope required on all worker handlers. |\n