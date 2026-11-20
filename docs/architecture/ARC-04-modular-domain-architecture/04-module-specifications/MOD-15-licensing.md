# MOD-15 — Subscription & Licensing Module Specification

**Module ID:** MOD-15  
**Tier:** Commercial Capabilities (P1)  
**Package:** `app.modules.licensing`  

---

## 1. Ownership & Boundaries
- **Owns:** Plans, entitlements, license keys, license evaluation.
- **Does Not Own:** User authentication credentials, database multi-tenancy rules.

## 2. Domain Model & Invariants
- **License Entity:** `License(license_id, organization_id, license_key, entitled_features, expires_at, is_revoked)`
  - Critical Boundary: Licensing governs commercial features, never basic security access.
  - Cryptographic key check: Forged or expired keys fail validity (`is_valid()`).

## 3. Public Contracts & Events
- **Provides:** `LicenseEvaluator` Protocol (`is_feature_entitled`).
- **Consumes:** `OrganizationReader`.
- **Emits:** `EntitlementUpdated` (EVT-017).
