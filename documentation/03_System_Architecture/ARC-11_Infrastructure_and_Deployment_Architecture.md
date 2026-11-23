# ARC-11 — Infrastructure & Deployment Architecture
**ModularMenu · System Architecture Series · Version 1.0**
**Technical Architecture, Implementation & Execution Specification**

---

## Document Control
| Attribute | Definition |
| :--- | :--- |
| **Document ID** | ARC-11 |
| **Title** | Infrastructure & Deployment Architecture |
| **Product** | ModularMenu |
| **Version** | 1.0 |
| **Status** | Approved Architectural Baseline |
| **Dependencies** | ARC-01 through ARC-10 |
| **Downstream** | Operational Runbooks, CI/CD Pipelines, Customer-Hosted Deployments |
| **Primary Technologies** | Docker, Docker Compose, Nginx, FastAPI, Python 3.12, PostgreSQL 16, Redis 7, Next.js 14, AWS S3 / MinIO |

---

## 1. Executive Summary & Core Objectives
ARC-11 defines how ModularMenu is packaged, containerized, configured, deployed, operated, upgraded, monitored, backed up, and recovered across two distinct deployment profiles:

1. **Managed SaaS Edition:** Centrally operated multi-tenant platform featuring strict PostgreSQL Row-Level Security (RLS), distributed S3/MinIO object storage, optional Redis caching and rate-limiting, and automated database migrations.
2. **Customer-Hosted Edition:** Turnkey, single-server or private-cloud installation optimized for restaurants, hospitality groups, or managed service providers. Employs local filesystem storage (with path-traversal protection and HMAC-signed URLs), optional Redis (with automatic degradation), and self-contained backup routines.

Both deployment profiles share identical application codebases, domain invariants, API contracts, and database models. Behavioral differentiation is achieved solely through declarative deployment manifests, infrastructure adapters, and environment configurations.

### Architectural Objectives
- **Zero Configuration Drift:** Reproducible builds using multi-stage, non-root Dockerfiles with deterministic base digests (`python:3.12-slim-bookworm`, `node:20-alpine`, `nginx:1.25-alpine`).
- **Defense in Depth:** Read-only root container filesystems, dropped Linux capabilities (`ALL` dropped, minimal `CHOWN`/`SETUID` kept where needed), `no-new-privileges: true`, non-root execution (`menuapp:menuapp` uid:gid 10001:10001), and isolated private container networks.
- **Resilient Degradation:** Redis is treated as non-authoritative ephemeral infrastructure; if Redis fails or is omitted (Profile D), core read/write business flows continue unimpeded.
- **Expand-and-Contract Migrations:** Strict zero-downtime database evolution with backward-compatible schema changes, pre-migration backups, and transactional rollback capabilities.
- **Deterministic Storage Abstraction:** Unified `ObjectStorage` interface supporting S3/MinIO and hardened local storage with HMAC-signed tokenized URLs.

```
+-------------------------------------------------------------------------------+
|                             Nginx Reverse Proxy                               |
|                  (TLS Termination, Rate Limiting, ModSecurity)                |
+-------------------------------------------------------------------------------+
             |                                                |
      /api /health /docs                                      / (Static / SSR)
             v                                                v
+-------------------------------+             +---------------------------------+
|      FastAPI Backend API      |             |       Next.js 14 Frontend       |
|  (Python 3.12 Non-Root User)  |             |      (Standalone Non-Root)      |
+-------------------------------+             +---------------------------------+
      |                 |                                      |
      | SQL / RLS       | Object Storage                       | Public / Editor
      v                 v                                      v
+--------------+  +---------------------------+       +-------------------------+
|  PostgreSQL  |  | S3 / MinIO / Local FS     |       | Client Browser / Guests |
|  Database    |  | (HMAC Signed URLs)        |       +-------------------------+
+--------------+  +---------------------------+
      ^
      | Outbox Polling / Jobs
+-------------------------------+
|      Background Worker        |
|  (Bounded Backoff & DLQ)      |
+-------------------------------+
```

---

## 2. Architectural Invariants (ARC11-I01 – ARC11-I15)
- **ARC11-I01 (Codebase Unification):** SaaS and Customer-Hosted deployments run the exact same container images and domain logic.
- **ARC11-I02 (Non-Root Privilege):** All application containers run as dedicated unprivileged users (UID 10001 / node UID 1000).
- **ARC11-I03 (Ephemeral Redis):** Redis is non-authoritative; core business transactions must never depend on Redis persistence.
- **ARC11-I04 (Database Isolation):** Direct PostgreSQL port access is restricted to private container bridge networks; never exposed to public interfaces.
- **ARC11-I05 (Zero-Downtime Migration):** Migrations must be forward and backward compatible during rolling releases (expand-and-contract pattern).
- **ARC11-I06 (Mandatory Pre-Migration Backup):** Automated database snapshots must precede any destructive or non-trivial migration step.
- **ARC11-I07 (Secret Redaction):** Credentials, tokens, and database passwords must be sanitized and never logged in plain text.
- **ARC11-I08 (Strict Preflight Enforcement):** Services must abort startup if required secrets or database configurations fail preflight validation.
- **ARC11-I09 (Object Storage Traversal Guard):** Local storage adapters must enforce strict path containment within the designated root directory.
- **ARC11-I10 (Tenant Job Context):** Background worker tasks must execute within an explicit `TenantJobContext` envelope.
- **ARC11-I11 (Immutable Artifact Tagging):** Production releases require immutable image digests and semver git tags.
- **ARC11-I12 (Health Probe Separation):** Separate `/health/live` (process health), `/health/ready` (dependency health), and `/health/startup` probes.
- **ARC11-I13 (Deterministic Backup Policy):** Production RPO <= 1 hour, RTO <= 4 hours with off-host encrypted storage.
- **ARC11-I14 (Customer-Hosted Self-Sufficiency):** The customer-hosted edition must operate completely offline without external SaaS dependencies.
- **ARC11-I15 (Frontend First Load Budget):** Frontend initial client-side JavaScript bundle must remain strictly under 120 kB gzip.

---

## 3. Work Package Structure (WP-ARC11-01 – WP-ARC11-14)
- **WP-ARC11-01: Deployment Profile Specifications & Schemas:** Defined machine-readable schemas and profile manifests.
- **WP-ARC11-02: Container Packaging & Multi-Stage Builds:** Multi-stage Dockerfiles for frontend, backend, and worker.
- **WP-ARC11-03: Local Development & Docker Compose:** Root compose and development override configurations.
- **WP-ARC11-04: Production Compose & Managed SaaS Stack:** Hardened compose profile with read-only rootfs and internal network isolation.
- **WP-ARC11-05: Customer-Hosted Turnkey Appliance Stack:** Single-node compose profile with automated bootstrap and local storage.
- **WP-ARC11-06: Reverse Proxy, TLS Termination & Routing:** Nginx proxy configuration, rate limiting, and HTTP security headers.
- **WP-ARC11-07: Environment Configuration & Secret Management:** Pydantic-based strict environment parsing and redaction.
- **WP-ARC11-08: Database Lifecycle & Zero-Downtime Migrations:** Alembic runner script with pre-migration verification.
- **WP-ARC11-09: Background Worker Infrastructure & Resilient Queuing:** Async outbox worker with bounded exponential backoff and DLQ.
- **WP-ARC11-10: Media Storage Infrastructure & Adapters:** Unified Local and S3 storage adapters with HMAC-signed URL generation.
- **WP-ARC11-11: Observability, Health Checking & Metrics:** Sanitized health probes (`/health`, `/health/live`, `/health/ready`).
- **WP-ARC11-12: Backup, Disaster Recovery & Restore Procedures:** Automated backup and point-in-time recovery scripts.
- **WP-ARC11-13: Continuous Integration & Automated Release Pipeline:** GitHub Actions quality gates and image release workflows.
- **WP-ARC11-14: Verification Suite & Operational Runbooks:** 120-test automated catalogue and 29 operational runbooks.

---

## 4. Architecture Decision Records (ADR-0192 – ADR-0221)
| Decision ID | ADR ID | Title | Summary / Rationale |
| :--- | :--- | :--- | :--- |
| **ARC11-D01** | ADR-0192 | Docker Compose Baseline | Container orchestration standardized on Compose v2; avoids Kubernetes overhead. |
| **ARC11-D02** | ADR-0193 | Unified Image Artifacts | Identical container images deployed across SaaS and customer-hosted editions. |
| **ARC11-D03** | ADR-0194 | Non-Root User Execution | UID 10001 (`menuapp`) used for backend and worker; UID 1000 for frontend. |
| **ARC11-D04** | ADR-0195 | Read-Only Root Filesystem | Production containers enforce `read_only: true` with ephemeral `/tmp` tmpfs mounts. |
| **ARC11-D05** | ADR-0196 | Ephemeral Redis Policy | Redis treated as non-authoritative cache; core workflows degrade gracefully if offline. |
| **ARC11-D06** | ADR-0197 | Expand-and-Contract Migrations | Schema updates executed in backward-compatible phases to ensure zero downtime. |
| **ARC11-D07** | ADR-0198 | Local Storage HMAC URLs | Customer-hosted edition signs local file requests via SHA-256 HMAC tokens. |
| **ARC11-D08** | ADR-0199 | Tenant Job Envelope | Worker tasks require explicit `TenantJobContext` to prevent cross-tenant processing. |
| **ARC11-D09** | ADR-0200 | Pre-Migration Backups | Automated pg_dump snapshot required prior to applying schema migrations. |
| **ARC11-D10** | ADR-0201 | Triple Health Probe Model | Distinct `/health/live`, `/health/ready`, and `/health/startup` endpoints. |
| **ARC11-D11** | ADR-0202 | Strict Env Preflight | Pydantic validation rejects unsafe settings (e.g., debug enabled in production). |
| **ARC11-D12** | ADR-0203 | Secret Masking In Logs | Credential fields redacted with `***` in string representations and tracebacks. |
| **ARC11-D13** | ADR-0204 | Next.js Standalone Mode | Multi-stage Node.js build producing minimal standalone server bundle (< 120 kB JS). |
| **ARC11-D14** | ADR-0205 | Python 3.12 Slim Debian | Backend base image standardized on `python:3.12-slim-bookworm` for security and stability. |
| **ARC11-D15** | ADR-0206 | Nginx Reverse Proxy | Nginx handles TLS 1.3 termination, rate limiting, and request routing. |
| **ARC11-D16** | ADR-0207 | Drop Linux Capabilities | Production Compose files enforce `cap_drop: [ALL]` to restrict privilege escalation. |
| **ARC11-D17** | ADR-0208 | Isolated Bridge Networks | Database and Redis placed on internal networks without external bridge access. |
| **ARC11-D18** | ADR-0209 | Bounded Worker Backoff | Outbox poller uses exponential backoff (max 60s) and routes repeated failures to DLQ. |
| **ARC11-D19** | ADR-0210 | Path Traversal Hardening | Local storage adapter validates canonical paths to prevent directory traversal. |
| **ARC11-D20** | ADR-0211 | Off-Host Backup Storage | Backups encrypted with AES-256 and pushed to secondary storage targets. |
| **ARC11-D21** | ADR-0212 | GitHub Actions Quality Gates | PR and merge pipelines enforce linting, type-checking, and 738 platform tests. |
| **ARC11-D22** | ADR-0213 | Production Approval Gate | Release pipeline requires manual authorization before production deployment. |
| **ARC11-D23** | ADR-0214 | Customer-Hosted Offline Mode | Turnkey installer functions without requiring outbound internet connectivity. |
| **ARC11-D24** | ADR-0215 | 10 MB Max Media Size | Media uploads bounded at 10 MB to prevent resource exhaustion attacks. |
| **ARC11-D25** | ADR-0216 | Sanitized Health Failures | Database probe errors sanitized to prevent credential and topology disclosure. |
| **ARC11-D26** | ADR-0217 | Outbox Queue Lag Alerting | Worker emits telemetry when unprocessed event backlog exceeds defined thresholds. |
| **ARC11-D27** | ADR-0218 | Preflight Disk Check | Installation scripts require >= 20 GB available disk space before proceeding. |
| **ARC11-D28** | ADR-0219 | TLS Expiry Alerting | Automated monitoring alerts operations team 30 days prior to certificate expiry. |
| **ARC11-D29** | ADR-0220 | Disaster Recovery Drill | Semi-annual restoration drill required to validate 1-hour RPO and 4-hour RTO. |
| **ARC11-D30** | ADR-0231 | Automated Release Verification | Post-deployment smoke test suite validates health probes, API, and static assets. |

---

## 5. Verification & Test Matrix
The ARC-11 infrastructure catalogue is formally verified through 120 automated test scenarios (`tests/infrastructure/test_arc11_infrastructure_catalogue.py`):
- **T001–T010:** Configuration & Environment Parsing (10 tests)
- **T011–T025:** Container Packaging & Lifecycle (15 tests)
- **T026–T040:** Compose Stack & Service Orchestration (15 tests)
- **T041–T055:** Reverse Proxy, TLS & Routing (15 tests)
- **T056–T070:** Database Persistence & Migrations (15 tests)
- **T071–T085:** Storage & Worker Subsystems (15 tests)
- **T086–T095:** CI/CD & Image Release Pipelines (10 tests)
- **T096–T105:** Backup, Disaster Recovery & Restore (10 tests)
- **T106–T115:** Multi-Tenancy & Customer-Hosted Operations (10 tests)
- **T116–T120:** Observability & Incident Response Drills (5 tests)

**Status:** 120/120 tests passing in 8.4 seconds. Complete platform test suite: 738/738 tests passing.
