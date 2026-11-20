# ARC-05 — Multi-Tenant Architecture & Isolation Model

**ModularMenu Architecture Series · Version 1.0.0**  
**Status: Approved Baseline & Implemented**

---

## 1. Executive Summary

ARC-05 establishes the multi-tenant architecture and security isolation model for ModularMenu. The primary architectural objective is **uncompromising tenant data isolation** (Priority P0) across both the shared-infrastructure Managed SaaS edition and the single-tenant Customer-Hosted Docker appliance edition, while sharing 100% domain and authorization logic parity.

In ModularMenu:
- The **Organization** is the primary tenant boundary.
- The **Restaurant** is a subordinate resource boundary within the organization.
- Tenancy is enforced through an **8-layer defense-in-depth model**:
  1. Identity & Session Verification
  2. Authoritative Server-Derived Tenant Context
  3. Fine-Grained Role & Branch Authorization
  4. Application & Domain Service Scoping
  5. Scoped Repository Filtering
  6. PostgreSQL Row-Level Security (RLS) Fail-Closed Policies
  7. Tenant-Scoped Storage Keys & Cache Namespaces
  8. Security Audit Logging & Anomaly Monitoring

---

## 2. Document Map

| Document ID | Title | Summary |
|---|---|---|
| `01-multi-tenancy-overview.md` | Multi-Tenancy Overview | Business drivers, core principles, and the 8-layer defense-in-depth model |
| `02-tenant-hierarchy.md` | Tenant Hierarchy | Multi-branch organizational structure, relationships, and scopes |
| `03-tenancy-isolation-model.md` | Tenancy Isolation Model | Shared database/shared schema vs customer-hosted appliance |
| `04-tenant-context-resolution.md` | Tenant Context Resolution | Trusted server-side TenantContext creation and propagation |
| `05-organization-membership.md` | Organization Membership | User identities, memberships, invitations, and revocation |
| `06-authorization-and-permissions.md` | Authorization & Permissions | Role hierarchy, permission vocabulary, and branch assignment |
| `07-resource-ownership.md` | Resource Ownership | 16-module resource ownership matrix and access boundaries |
| `08-backend-tenant-enforcement.md` | Backend Tenant Enforcement | Request lifecycle, use case enforcement, and repository scoping |
| `09-postgresql-rls-architecture.md` | PostgreSQL RLS Architecture | Transaction-local settings, DDL policies, and fail-closed security |
| `10-database-ownership-constraints.md` | Relational Constraints | Composite foreign keys and cross-tenant relationship prevention |
| `11-tenant-storage-isolation.md` | Storage & Media Isolation | Scoped object keys, upload validation, and private signed URLs |
| `12-tenant-cache-isolation.md` | Cache Isolation Architecture | Prefixed cache keys, eviction policies, and TanStack query safety |
| `13-public-menu-isolation.md` | Public Menu Isolation | Published-only read model and strict draft protection |
| `14-background-job-isolation.md` | Background Job Isolation | TenantJobContext, connection cleanup, and system worker separation |
| `15-tenant-lifecycle.md` | Tenant Lifecycle | Provisioning, active operation, suspension grace, and offboarding |
| `16-frontend-tenant-management.md` | Frontend Tenant Management | Organization switcher, route guards, and query key management |
| `17-audit-and-monitoring.md` | Audit & Security Monitoring | Security events, role changes, anomaly detection, and redaction |
| `18-threat-model.md` | Threat Model Analysis | STRIDE evaluation, 18 threat vectors (ARC05-TH01–TH18) |
| `19-security-testing.md` | Security Testing Strategy | Test environment, IDOR testing, RLS testing, and attack harness |
| `20-verification-and-validation.md` | Verification & Validation | Quality gates, CI pipeline, and automated compliance verification |
| `21-implementation-work-packages.md` | Implementation Work Packages | Completed work packages WP-ARC05-01 through WP-ARC05-12 |
| `22-risk-register.md` | Tenancy Risk Register | 20 security risks (ARC05-R01–R20) and enforceable mitigations |
| `23-architecture-decisions.md` | Architecture Decisions | 20 approved architectural decisions (ARC05-D01–D20 / ADR-0044–0063) |
| `24-compliance-report.md` | Compliance & Release Report | Traceability matrix, sign-off criteria, and release approval |

---

## 3. Implementation Artifacts

- **Tenant Manifests:**
  - `backend/architecture/tenant_owned_resources.yaml`
  - `backend/architecture/rls_coverage.yaml`
- **Application & Domain Code:**
  - `backend/app/shared/application/tenant_context.py`
  - `backend/app/shared/application/tenant_resolver.py`
  - `backend/app/shared/application/authorization.py`
  - `backend/app/shared/domain/permissions.py`
  - `backend/app/shared/domain/tenant_exceptions.py`
- **Infrastructure Adapters:**
  - `backend/app/infrastructure/database/tenant_session.py`
  - `backend/app/infrastructure/database/rls.py`
  - `backend/app/infrastructure/database/roles.py`
  - `backend/app/shared/infrastructure/tenant_storage.py`
  - `backend/app/shared/infrastructure/tenant_cache.py`
  - `backend/app/shared/infrastructure/tenant_database.py`
  - `backend/app/infrastructure/workers/tenant_job_context.py`
- **Automated Verification:**
  - `tests/tenant_isolation/test_arc05_tenant_catalogue.py` (50 test scenarios passing)
