# Devlog-006: ARC-05 Multi-Tenant Architecture & Isolation Model
**Date:** 2026-11-20  
**Milestone:** ARC-05 Multi-Tenant Architecture  
**Git Tag:** `v1.0.0-arc05`  
**Status:** Approved & Implemented  
**Author:** ModularMenu Architecture Team  

---

## 1. Tenancy Model: Organization as Sovereign Boundary

ARC-05 established the formal multi-tenancy model:
- **Organization (`organizations`):** The primary legal, commercial, and tenant isolation boundary.
- **Restaurant (`restaurants`):** A subordinate branch resource within an organization.
- **Rule:** A tenant cannot exist without an organization; restaurant branches share organizational ownership and billing boundaries while maintaining branch-level scoping.

---

## 2. Eight-Layer Defense in Depth

To prevent any cross-tenant data leakage, ARC-05 engineered an 8-layer security perimeter:
1. **Perimeter 1 (Host & Route Ingress):** Hostname and subdomain parsing.
2. **Perimeter 2 (Authentication & Token Verification):** Cryptographic verification of JWT session tokens.
3. **Perimeter 3 (Server-Derived TenantContext):** Immutable, tamper-proof context extracted exclusively from server session records.
4. **Perimeter 4 (Application Authorization):** Fine-grained RBAC and restaurant membership checks.
5. **Perimeter 5 (Repository & Query Scoping):** Explicit `organization_id` filtering on all tenant queries.
6. **Perimeter 6 (PostgreSQL Row-Level Security):** Database-level fail-closed RLS policies.
7. **Perimeter 7 (Object Storage Prefixing):** S3 object paths prefixed by `media/organizations/{org_id}/...`.
8. **Perimeter 8 (Cache & Worker Isolation):** Redis cache namespaces and background worker job contexts.

---

## 3. Public Diner Routing Decoupling

A critical architectural achievement:
- Public dining guests scanning table QR codes **do not authenticate as tenants**.
- Public delivery endpoints resolve exclusively published, frozen menu snapshots (`MOD-13`), completely bypassing tenant authorization and normalized draft tables (`MOD-12`).
- This guarantees zero draft leakage and enables aggressive CDN caching without compromising tenant security.

---

## 4. Verification & Release

- **50-Test Security Catalogue (ARC05-T001 to ARC05-T050):** Covering cross-tenant isolation, IDOR prevention, RLS verification, and cache separation.
- **Total Backend Tests:** **144 passing tests** (100% pass rate).
- **Decision Records:** `ADR-0044` through `ADR-0063` recorded in `docs/decisions/decision-register.md`.
