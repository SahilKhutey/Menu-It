# FCD-13 · Document 09 — End-to-End Platform Journeys Validation

## 1. Objective
Validates that foundational user journeys operate across the customer web app, administrative dashboard, API, database, and background processing systems.

---

## 2. Foundational Platform Journeys

### Journey A — Organization Onboarding & Membership
- **Flow:** User registers -> Organization is provisioned -> Membership assigned with `owner` role -> Authenticated session created -> Authoritative `TenantContext` resolved.
- **Verification:** Verified via backend registration and tenant resolution tests (`test_organization_provisioning.py`, `test_identity_tenant_security_chain.py`).

### Journey B — Restaurant Creation & Scope Validation
- **Flow:** Authenticated user creates a restaurant profile -> Organization ownership validated -> Database constraints enforce composite foreign keys -> Profile saved.
- **Verification:** Verified via `test_restaurant_profile_persistence.py` and `test_restaurant_profile_rls.py`.

### Journey C — Public Menu Discovery & Error Resilience
- **Flow:** Customer visits public URL (`/r/{slug}`) -> Menu-It web application resolves public profile -> Non-existent slugs render safe 404 UI without leaking backend errors.
- **Verification:** Verified via Playwright E2E test `tests/e2e/journeys.spec.ts` (`JNY-06 & JNY-11`).

### Journey D — Asynchronous Processing & Outbox Flow
- **Flow:** Business mutation stages outbox event -> Active transaction commits -> Worker dispatches task -> Idempotency verified -> Audit logged.
- **Verification:** Verified via `test_persistence_and_outbox_integration.py` and `test_async_infrastructure_integration.py`.

---

## 3. Journey Verification Matrix

| Journey ID | Title | Key Assertion | Verification Status |
| :--- | :--- | :--- | :---: |
| `JNY-01` | Customer Web App Discovery | Public landing page responds HTTP 200 | **PASSED** |
| `JNY-02` | Admin Portal Route Protection | Direct navigation without session redirects or blocks | **PASSED** |
| `JNY-03` | Non-Existent Slug Resilience | Public route handles 404 without crashing | **PASSED** |
| `JNY-04` | Asynchronous Task Delivery | Worker executes task and invalidates cache | **PASSED** |
| `JNY-05` | Universal Response Envelope | Error details adhere to structured API envelope | **PASSED** |

---

## 4. Automation Artifacts
- Playwright E2E Suite: `tests/e2e/journeys.spec.ts` & `tests/e2e/critical-flows.spec.ts`.
- Deployment Smoke Test: `tests/deployment/smoke.py`.
