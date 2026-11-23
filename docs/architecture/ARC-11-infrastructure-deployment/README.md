# ARC-11 — Infrastructure & Deployment Architecture Documentation Suite
**ModularMenu · System Architecture Series · Version 1.0**

This directory contains the complete technical architecture specification, deployment model definitions, operational guidelines, and verification criteria for **ARC-11: Infrastructure & Deployment Architecture**.

## Document Series Index
| Document ID | Title | Scope & Purpose |
| :--- | :--- | :--- |
| [01-infrastructure-overview.md](01-infrastructure-overview.md) | Infrastructure Overview | High-level topology, SaaS vs Customer-Hosted duality, shared core engine. |
| [02-deployment-profiles.md](02-deployment-profiles.md) | Deployment Profiles | Formal specification of Profiles A (Dev), B (CI/CD), C (SaaS), and D (Customer-Hosted). |
| [03-infrastructure-invariants.md](03-infrastructure-invariants.md) | Infrastructure Invariants | Enforceable rules ARC11-I01 through ARC11-I15. |
| [04-container-architecture.md](04-container-architecture.md) | Container Architecture | Multi-stage Dockerfiles, non-root users (UID 10001/1000), base image standards. |
| [05-compose-orchestration.md](05-compose-orchestration.md) | Compose Orchestration | Docker Compose v2 profiles, services, network topologies, volume persistence. |
| [06-reverse-proxy-and-tls.md](06-reverse-proxy-and-tls.md) | Reverse Proxy & TLS | Nginx routing, TLS 1.3 termination, HTTP security headers, rate limiting. |
| [07-configuration-and-secrets.md](07-configuration-and-secrets.md) | Configuration & Secrets | Pydantic strict settings, preflight validation, secret masking in logs. |
| [08-database-lifecycle.md](08-database-lifecycle.md) | Database Lifecycle | PostgreSQL 16 management, Alembic migrations, expand-and-contract zero-downtime rules. |
| [09-worker-and-queuing.md](09-worker-and-queuing.md) | Worker & Queuing | Outbox worker architecture, bounded backoff, DLQ handling, TenantJobContext. |
| [10-storage-architecture.md](10-storage-architecture.md) | Storage Architecture | ObjectStorage protocol, LocalStorageAdapter (HMAC signed URLs), S3StorageAdapter. |
| [11-observability-and-health.md](11-observability-and-health.md) | Observability & Health | Triple health probe model (/live, /ready, /startup), sanitized error handling. |
| [12-backup-and-disaster-recovery.md](12-backup-and-disaster-recovery.md) | Backup & Disaster Recovery | RPO <= 1h, RTO <= 4h, encrypted pg_dump, off-host backups, restoration drills. |
| [13-ci-cd-and-release-engineering.md](13-ci-cd-and-release-engineering.md) | CI/CD & Release Engineering | GitHub Actions pipelines, quality gates (738 tests), automated image builds. |
| [14-customer-hosted-architecture.md](14-customer-hosted-architecture.md) | Customer-Hosted Architecture | Turnkey appliance design, automated offline installation, local data ownership. |
| [15-saas-multi-tenant-infrastructure.md](15-saas-multi-tenant-infrastructure.md) | SaaS Multi-Tenant Infrastructure | Row-Level Security, tenant provisioning, shared infrastructure operations. |
| [16-network-and-firewall.md](16-network-and-firewall.md) | Network & Firewall | Isolated container networks, port exposure rules, ingress/egress filtering. |
| [17-security-and-hardening.md](17-security-and-hardening.md) | Security & Hardening | Read-only rootfs, drop Linux capabilities, non-root execution, vulnerability scanning. |
| [18-resource-sizing-and-capacity.md](18-resource-sizing-and-capacity.md) | Resource Sizing & Capacity | CPU, memory, and disk requirements across development, SaaS, and customer hosts. |
| [19-performance-and-benchmarking.md](19-performance-and-benchmarking.md) | Performance & Benchmarking | API response latency (< 100ms p95), query latency, frontend bundle budget (< 120 kB). |
| [20-high-availability-and-resilience.md](20-high-availability-and-resilience.md) | High Availability & Resilience | Ephemeral Redis degradation, container auto-restart, automated recovery. |
| [21-data-retention-and-purging.md](21-data-retention-and-purging.md) | Data Retention & Purging | Backup rotation (7 daily, 4 weekly, 12 monthly), outbox cleanup, audit logs. |
| [22-migration-and-upgrade-strategy.md](22-migration-and-upgrade-strategy.md) | Migration & Upgrade Strategy | Multi-version upgrade paths, backward compatibility, rollback execution. |
| [23-incident-management-framework.md](23-incident-management-framework.md) | Incident Management Framework | Severity classifications (P0-P3), escalation matrices, post-mortem templates. |
| [24-audit-logging-and-compliance.md](24-audit-logging-and-compliance.md) | Audit Logging & Compliance | Access logging, configuration change tracking, regulatory compliance controls. |
| [25-testing-and-verification-strategy.md](25-testing-and-verification-strategy.md) | Testing & Verification Strategy | 120 automated test scenarios (T001-T120), execution methodology, CI integration. |
| [26-verification-criteria-assessment.md](26-verification-criteria-assessment.md) | Verification Criteria Assessment | Formal assessment of Verification Criteria VF-01 through VF-25 (100% verified). |
| [27-validation-criteria-assessment.md](27-validation-criteria-assessment.md) | Validation Criteria Assessment | Formal assessment of Validation Criteria VAL-01 through VAL-10. |
| [28-work-package-breakdown.md](28-work-package-breakdown.md) | Work Package Breakdown | WP-ARC11-01 through WP-ARC11-14 detailed deliverables and status. |
| [29-architecture-decisions.md](29-architecture-decisions.md) | Architecture Decisions | ADR-0192 through ADR-0221 (ARC11-D01 through ARC11-D30) register. |
| [30-risk-and-mitigation-register.md](30-risk-and-mitigation-register.md) | Risk & Mitigation Register | Operational risk analysis (R-01 through R-12) and mitigation controls. |
| [31-cost-and-operational-envelope.md](31-cost-and-operational-envelope.md) | Cost & Operational Envelope | TCO breakdown, infrastructure costs, scaling economics. |
| [32-runbook-and-operations-index.md](32-runbook-and-operations-index.md) | Runbook & Operations Index | Directory of 29 operational guides, setup procedures, and emergency runbooks. |
| [33-traceability-matrix.md](33-traceability-matrix.md) | Traceability Matrix | End-to-end mapping of invariants, requirements, tests, ADRs, and runbooks. |
| [34-completion-report.md](34-completion-report.md) | Completion Report | Final executive sign-off, verification summary, and release authorization. |\n