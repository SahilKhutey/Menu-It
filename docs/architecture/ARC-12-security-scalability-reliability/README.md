# ARC-12 — Security, Scalability & Reliability Architecture Specification Suite
**ModularMenu · System Architecture Series · Version 1.0**

This directory contains the complete 47-document specification suite detailing the security engineering, application scalability, and operational reliability architecture for ModularMenu.

## Document Directory Structure

### Section 1: Foundations & Principles
- [01-architecture-overview.md](01-architecture-overview.md): Executive summary, core objectives, and platform architectural posture.
- [02-security-engineering-principles.md](02-security-engineering-principles.md): Defense-in-depth, fail-closed defaults, zero trust tenant boundary, and least privilege.
- [03-scalability-principles.md](03-scalability-principles.md): Stateless compute, read/write splitting, tiered caching, and bundle minimization.
- [04-reliability-principles.md](04-reliability-principles.md): Graceful degradation, circuit breaking, bounded timeouts, and transactional outbox.
- [05-architectural-invariants.md](05-architectural-invariants.md): Formal definition of ARC12-I01 through ARC12-I20 invariants.

### Section 2: Identity, Authentication & Authorization
- [06-identity-and-authentication.md](06-identity-and-authentication.md): Argon2id password hashing, credential validation, and brute force defenses.
- [07-session-lifecycle-and-tokens.md](07-session-lifecycle-and-tokens.md): Cryptographic CSPRNG tokens, immediate session rotation, and `__Host-` cookies.
- [08-centralized-authorization-and-rbac.md](08-centralized-authorization-and-rbac.md): Role-to-permission mapping, multi-restaurant scoping, and FastAPI guard dependencies.

### Section 3: Multi-Tenant Boundary Isolation
- [09-multi-tenant-isolation-and-rls.md](09-multi-tenant-isolation-and-rls.md): PostgreSQL Row-Level Security, FORCE RLS, non-bypass role, and context variable setup.
- [10-cross-tenant-boundary-defense.md](10-cross-tenant-boundary-defense.md): Server-side tenant resolver, composite foreign keys, and connection pool cleanup.

### Section 4: API & Application Security Hardening
- [11-api-security-and-input-validation.md](11-api-security-and-input-validation.md): Parameterized queries, schema validation, and cursor pagination bounds.
- [12-injection-and-xss-defense.md](12-injection-and-xss-defense.md): SQL injection neutralization, HTML sanitization, and React/Next.js XSS prevention.
- [13-csrf-and-cors-controls.md](13-csrf-and-cors-controls.md): Anti-CSRF token verification, SameSite cookie attributes, and CORS origin allowlists.
- [14-ssrf-defense-and-network-boundaries.md](14-ssrf-defense-and-network-boundaries.md): Outbound request validation, private IP blacklisting, and redirect inspection.

### Section 5: Public Menu & Customization Isolation
- [15-public-menu-security-and-isolation.md](15-public-menu-security-and-isolation.md): Published immutable snapshots, draft isolation, and watermark protection.
- [16-customization-and-theme-sandboxing.md](16-customization-and-theme-sandboxing.md): JSON schema component validation, token hex regexes, and CSS token scoping.

### Section 6: Media Upload & Asset Pipeline
- [17-media-upload-and-storage-security.md](17-media-upload-and-storage-security.md): MIME type allowlists, magic byte verification, path traversal checks, and signed URLs.
- [18-image-processing-and-decompression-guards.md](18-image-processing-and-decompression-guards.md): 10 MB payload ceiling, 25 megapixel dimension limits, and WebP transcoding.

### Section 7: Webhooks, Inter-Service & Audit
- [19-webhook-cryptographic-security.md](19-webhook-cryptographic-security.md): HMAC SHA-256 signature verification, 300s timestamp tolerance, and replay protection.
- [20-inter-service-communication-security.md](20-inter-service-communication-security.md): Mutual TLS, private Docker networks, and internal API gateway routing.
- [21-audit-logging-and-integrity.md](21-audit-logging-and-integrity.md): Immutable append-only audit ledger, schema validation, and tamper-evident storage.
- [22-credential-masking-and-data-protection.md](22-credential-masking-and-data-protection.md): Automatic regex masking of passwords and bearer tokens in logs and traces.

### Section 8: Infrastructure & Secrets Security
- [23-container-and-os-hardening.md](23-container-and-os-hardening.md): Non-root execution (UID 1001/1000), read-only rootfs, and dropped Linux capabilities.
- [24-network-security-and-tls.md](24-network-security-and-tls.md): TLS 1.3 termination, Nginx reverse proxy configuration, and HSTS headers.
- [25-secrets-management-and-lifecycle.md](25-secrets-management-and-lifecycle.md): Environment variable injection, no baked image secrets, and automated secret rotation.
- [26-vulnerability-management-and-sbom.md](26-vulnerability-management-and-sbom.md): Dependency vulnerability scanning, Trivy container scans, and CycloneDX/SPDX SBOMs.

### Section 9: Application Scalability & Caching
- [27-application-scalability-and-concurrency.md](27-application-scalability-and-concurrency.md): Stateless API concurrency, uvicorn worker pools, and async I/O.
- [28-multi-tier-caching-architecture.md](28-multi-tier-caching-architecture.md): In-memory L1 cache, Redis L2 cache, Edge CDN L3, and Cache-Control headers.
- [29-frontend-performance-and-bundle-budget.md](29-frontend-performance-and-bundle-budget.md): 120 kB gzip JS budget, dynamic chunking, Next.js optimization, and Core Web Vitals.

### Section 10: Database & Worker Scalability
- [30-database-scalability-and-indexing.md](30-database-scalability-and-indexing.md): Composite B-tree indexing on tenant columns, query plans, and partition readiness.
- [31-connection-pooling-and-query-optimization.md](31-connection-pooling-and-query-optimization.md): Asyncpg connection pool tuning, timeout envelopes, and pool sizing math.
- [32-worker-scalability-and-outbox-processing.md](32-worker-scalability-and-outbox-processing.md): Transactional outbox polling, batch processing, and horizontal worker scaling.
- [33-rate-limiting-and-traffic-shaping.md](33-rate-limiting-and-traffic-shaping.md): Token bucket algorithm, sliding window counters, and IP/tenant tiered limits.
- [34-load-shedding-and-backpressure.md](34-load-shedding-and-backpressure.md): HTTP 429 Retry-After signaling, queue depth thresholds, and CPU/memory shedding.

### Section 11: Resilience, Circuit Breakers & Disaster Recovery
- [35-service-continuity-and-graceful-degradation.md](35-service-continuity-and-graceful-degradation.md): Redis offline fallback, static menu fallbacks, and local storage resilience.
- [36-circuit-breakers-and-resilience-patterns.md](36-circuit-breakers-and-resilience-patterns.md): Three-state circuit breaker (Closed/Open/Half-Open) for third-party integrations.
- [37-retries-backoff-and-timeouts.md](37-retries-backoff-and-timeouts.md): Exponential backoff with uniform jitter, bounded attempts, and client timeouts.
- [38-dead-letter-queues-and-poison-pills.md](38-dead-letter-queues-and-poison-pills.md): Poison pill quarantine after 8 attempts, DLQ ledger, and manual retry tools.
- [39-database-failover-and-recovery.md](39-database-failover-and-recovery.md): Streaming replication, automated health checks, and connection reset routines.
- [40-disaster-recovery-and-pitr.md](40-disaster-recovery-and-pitr.md): RPO <= 1h, RTO <= 4h, point-in-time recovery, off-host backups, and restoration drills.

### Section 12: Verification, Validation, Decisions & Governance
- [41-security-verification-criteria-vf01-vf32.md](41-security-verification-criteria-vf01-vf32.md): 32 formal verification activities and evidentiary criteria.
- [42-validation-scenarios-val01-val15.md](42-validation-scenarios-val01-val15.md): 15 comprehensive operational validation exercises.
- [43-automated-test-catalogue-t001-t150.md](43-automated-test-catalogue-t001-t150.md): 150 automated test scenarios across 13 engineering domains.
- [44-work-package-breakdown-wp01-wp15.md](44-work-package-breakdown-wp01-wp15.md): 15 work packages detailing engineering execution.
- [45-architecture-decision-records-d01-d35.md](45-architecture-decision-records-d01-d35.md): 35 ADRs (ADR-0222 to ADR-0256) governing architectural choices.
- [46-threat-model-and-risk-register.md](46-threat-model-and-risk-register.md): STRIDE threat assessment, risk scoring, and countermeasure matrix.
- [47-completion-report.md](47-completion-report.md): Formal closure, compliance verification, and handoff to production operations.
