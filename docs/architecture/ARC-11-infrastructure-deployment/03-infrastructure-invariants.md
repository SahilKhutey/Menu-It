# 03 — Infrastructure Invariants
**ARC-11: Infrastructure & Deployment Architecture**

## Architectural Invariants (ARC11-I01 – ARC11-I15)

1. **ARC11-I01 (Codebase Unification):** SaaS and Customer-Hosted deployments run the exact same container images and domain logic. No branch-based divergence.
2. **ARC11-I02 (Non-Root Privilege):** All application containers run as dedicated unprivileged users (UID 10001 / node UID 1000). Root execution is strictly prohibited.
3. **ARC11-I03 (Ephemeral Redis):** Redis is non-authoritative; core business transactions must never depend on Redis persistence. Outages must trigger graceful degradation.
4. **ARC11-I04 (Database Isolation):** Direct PostgreSQL port access is restricted to private container bridge networks; never exposed to public interfaces.
5. **ARC11-I05 (Zero-Downtime Migration):** Migrations must be forward and backward compatible during rolling releases (expand-and-contract pattern).
6. **ARC11-I06 (Mandatory Pre-Migration Backup):** Automated database snapshots must precede any destructive or non-trivial migration step.
7. **ARC11-I07 (Secret Redaction):** Credentials, tokens, and database passwords must be sanitized and never logged in plain text or emitted in error responses.
8. **ARC11-I08 (Strict Preflight Enforcement):** Services must abort startup if required secrets or database configurations fail preflight validation.
9. **ARC11-I09 (Object Storage Traversal Guard):** Local storage adapters must enforce strict path containment within the designated root directory.
10. **ARC11-I10 (Tenant Job Context):** Background worker tasks must execute within an explicit `TenantJobContext` envelope.
11. **ARC11-I11 (Immutable Artifact Tagging):** Production releases require immutable image digests and semver git tags.
12. **ARC11-I12 (Health Probe Separation):** Separate `/health/live` (process health), `/health/ready` (dependency health), and `/health/startup` probes.
13. **ARC11-I13 (Deterministic Backup Policy):** Production RPO <= 1 hour, RTO <= 4 hours with off-host encrypted storage.
14. **ARC11-I14 (Customer-Hosted Self-Sufficiency):** The customer-hosted edition must operate completely offline without external SaaS dependencies.
15. **ARC11-I15 (Frontend First Load Budget):** Frontend initial client-side JavaScript bundle must remain strictly under 120 kB gzip.\n