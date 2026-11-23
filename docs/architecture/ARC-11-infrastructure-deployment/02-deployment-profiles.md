# 02 — Deployment Profiles
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Overview of Deployment Profiles
ModularMenu defines four official deployment profiles codified in `infrastructure/manifests/deployment_profiles.yaml`:

### Profile A: Local Development (`profile_a_local_dev`)
- **Target:** Developer workstations.
- **Characteristics:** Hot reload enabled, debug logging, local SQLite/PostgreSQL, mocked services.
- **Security:** Relaxed cookies (non-HTTPS), auto-generated development secrets.
- **Compose Manifest:** `compose.yaml` + `compose.dev.yaml`.

### Profile B: CI/CD Quality Gates (`profile_b_ci_pipeline`)
- **Target:** Automated testing runners (GitHub Actions).
- **Characteristics:** Ephemeral containers, automated test execution (738 tests), strict linting and typechecking.
- **Security:** Synthetic disposable secrets, ephemeral databases, automated cleanup.

### Profile C: Managed SaaS Production (`profile_c_saas_production`)
- **Target:** ModularMenu centrally managed multi-tenant cloud.
- **Isolation Level:** Shared database with PostgreSQL Row-Level Security (RLS) (`multi_tenant_rls_isolated`).
- **Storage:** Amazon S3 / Cloudflare R2 / MinIO with tenant prefix partitioning (`tenants/{org_id}/...`).
- **Cache:** Distributed Redis cluster for rate limiting and ephemeral cache.
- **Security:** `read_only: true` container root filesystems, dropped Linux capabilities (`cap_drop: [ALL]`), non-root users (`10001:10001`), strict TLS 1.3.

### Profile D: Customer-Hosted Turnkey Appliance (`profile_d_customer_hosted_production`)
- **Target:** Restaurant on-premise hardware or customer-managed VPS.
- **Isolation Level:** Dedicated physical/virtual instance (`single_tenant_dedicated`).
- **Storage:** Local filesystem (`/var/lib/modularmenu/media`) with HMAC SHA-256 URL signing.
- **Cache:** Optional single-node Redis; graceful in-memory fallback when omitted.
- **Security:** Automated turnkey configuration, local network isolation, self-signed or Let's Encrypt TLS.\n