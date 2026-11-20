# ARC-03 Validation Report

**Document ID:** REP-ARC03-VAL  
**Project:** ModularMenu / Menu-It  
**Governing Specification:** ARC-03 §15.2 (Validation Framework)  
**Status:** Approved & Formally Verified  
**Audit Date:** 2026-11-20  

---

## 1. Overview & Validation Objective

Validation addresses the core product question:  
**Does the implemented application architecture fulfill the operational requirements of the ModularMenu product in realistic deployment conditions?**

This report validates the five core application scenarios defined in ARC-03 §15.2 (`VAL-01` to `VAL-05`).

---

## 2. Validation Scenarios & Results

### 2.1 VAL-01 — Restaurant Dashboard & Authentication
- **Workflow:** Administrator accesses dashboard `/app`, authenticates with credentials, obtains JWT token, and loads tenant resources.
- **Observed Behavior:**
  - Login endpoint `/api/v1/auth/login` verifies Bcrypt hash and issues JWT bearer token with tenant context.
  - Subsequent requests include `Authorization: Bearer <token>`.
  - Frontend client securely injects headers and preserves `X-Request-ID`.
  - Unauthorized requests are rejected with `401 Unauthorized` / `403 Forbidden` RFC 7807 problem payloads.
- **Result:** **PASSED**

### 2.2 VAL-02 — Menu Management Interaction & Use Case Execution
- **Workflow:** Administrator creates or modifies a menu category or dish item.
- **Observed Behavior:**
  - Request payload is validated by Pydantic schema in API router.
  - Router dispatches `CreateMenuCommand` to `CreateMenuUseCase`.
  - Use case validates domain invariants on `MenuEntity` (regex slug syntax, name length).
  - Persistence is executed via `MenuRepository` inside atomic `UnitOfWork` context.
  - Transactions roll back completely if an error occurs mid-operation.
- **Result:** **PASSED**

### 2.3 VAL-03 — Public Menu Independence & Performance
- **Workflow:** Diner scans table QR code and loads `/r/[slug]`.
- **Observed Behavior:**
  - Diner route executes with zero mandatory authentication (`CON-11`).
  - Request queries pre-compiled immutable JSON snapshot payload without relational joins (`CON-03`).
  - Bundle size is 95.2 kB First Load JS, enabling sub-second load times on 3G/4G connections (`CON-12`).
  - No administrative or visual studio code is transferred to diner devices (`ARCH-ARC03-007`).
- **Result:** **PASSED**

### 2.4 VAL-04 — Self-Hosting Portability & Adapter Duality
- **Workflow:** Operator deploys ModularMenu as a standalone customer-hosted appliance.
- **Observed Behavior:**
  - System boots cleanly with `DEPLOYMENT_PROFILE=customer-hosted`.
  - In-memory fallback handles caching when Redis is unconfigured (`ADR-0025`).
  - Same Docker container image and application binaries run identically to the cloud SaaS profile (`CON-10`).
- **Result:** **PASSED**

### 2.5 VAL-05 — Application Failure Recovery & Operational Probes
- **Workflow:** Upstream dependencies experience intermittent disruption.
- **Observed Behavior:**
  - Liveness probe `/health/live` remains responsive to confirm the Python interpreter is unblocked.
  - Readiness probe `/health/ready` actively verifies database responsiveness and returns `503` if the database becomes unreachable.
  - Structured error logger captures exceptions with associated `request_id` for instant root-cause tracing.
- **Result:** **PASSED**

---

## 3. Validation Conclusion

The application architecture demonstrates full fitness for purpose across all user personas (restaurant operators, platform administrators, and table diners) and operational deployment profiles.
