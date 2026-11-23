# 29 — Architecture Decisions Register
**ARC-11: Infrastructure & Deployment Architecture**

## Summary of Decisions ADR-0192 through ADR-0221 (ARC11-D01 – ARC11-D30)
- **ADR-0192 (ARC11-D01):** Docker Compose v2 as the primary orchestration engine.
- **ADR-0193 (ARC11-D02):** Unified container images across SaaS and customer-hosted editions.
- **ADR-0194 (ARC11-D03):** Non-root user execution (`UID 10001` menuapp, `UID 1000` node).
- **ADR-0195 (ARC11-D04):** Read-only root filesystem with ephemeral tmpfs mounts.
- **ADR-0196 (ARC11-D05):** Ephemeral Redis policy with graceful degradation.
- **ADR-0197 (ARC11-D06):** Expand-and-contract zero-downtime database migrations.
- **ADR-0198 (ARC11-D07):** HMAC SHA-256 signed URLs for local filesystem storage.
- **ADR-0199 (ARC11-D08):** TenantJobContext envelope required for all worker jobs.
- **ADR-0200 (ARC11-D09):** Mandatory pre-migration backup before applying schema updates.
- **ADR-0201 (ARC11-D10):** Triple health probe model (`/live`, `/ready`, `/startup`).
- **ADR-0202 (ARC11-D11):** Strict Pydantic environment configuration preflight.
- **ADR-0203 (ARC11-D12):** Secret masking and redaction in logs and tracebacks.
- **ADR-0204 (ARC11-D13):** Next.js standalone output mode for minimal bundle footprint.
- **ADR-0205 (ARC11-D14):** Python 3.12 slim Debian Bookworm base image.
- **ADR-0206 (ARC11-D15):** Nginx reverse proxy for TLS termination and rate limiting.
- **ADR-0207 (ARC11-D16):** Drop all Linux capabilities (`cap_drop: [ALL]`).
- **ADR-0208 (ARC11-D17):** Isolated internal bridge network for database and cache.
- **ADR-0209 (ARC11-D18):** Bounded exponential backoff and dead-letter queue in worker.
- **ADR-0210 (ARC11-D19):** Path traversal guard in local storage adapter.
- **ADR-0211 (ARC11-D20):** AES-256 encrypted off-host backup storage.
- **ADR-0212 (ARC11-D21):** CI/CD quality gates enforcing 100% test pass rate.
- **ADR-0213 (ARC11-D22):** Manual approval gate for production releases.
- **ADR-0214 (ARC11-D23):** Air-gapped offline support for customer-hosted installations.
- **ADR-0215 (ARC11-D24):** 10 MB maximum upload limit for media assets.
- **ADR-0216 (ARC11-D25):** Sanitized error messages in health check endpoints.
- **ADR-0217 (ARC11-D26):** Transactional outbox backlog growth alerting.
- **ADR-0218 (ARC11-D27):** Preflight disk space verification (>= 20 GB).
- **ADR-0219 (ARC11-D28):** TLS certificate expiry alerting at 30 days.
- **ADR-0220 (ARC11-D29):** Semi-annual disaster recovery restore drills.
- **ADR-0221 (ARC11-D30):** Automated post-deployment release verification smoke tests.\n