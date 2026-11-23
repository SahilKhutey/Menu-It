# 15 — SaaS Multi-Tenant Infrastructure
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Multi-Tenant Tenancy Model
- Managed SaaS operates as a shared database and shared schema model with PostgreSQL Row-Level Security (RLS) enforcement.
- Tenant isolation is strictly maintained at the query level via `current_setting('app.current_org_id')`.
- Media storage isolates tenants via dedicated object prefixes: `tenants/{organization_id}/...`.
- Automated tenant onboarding and deprovisioning workflows ensure zero residual data contamination.\n