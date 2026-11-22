# ARC-08 §19 — Security & Tenant Isolation

## 1. Tenant Boundary Enforcement (P0 Security)
- Every query joins `Restaurant` and asserts `Restaurant.organization_id == tenant.organization_id`.
- Cross-tenant requests to access another restaurant's draft, preview, or revision history return HTTP 404 (Not Found) to prevent resource enumeration.
- Tenant ID forgery in JSON payloads is completely ignored; authorization context is derived exclusively from server-verified session JWT tokens.

## 2. Injection & XSS Mitigations
- Disallow HTML strings, `<script>` tags, event handlers (`onload`, `onerror`), and `javascript:` URIs.
- Style overrides are constrained strictly to token values; raw CSS selectors or declarations are rejected.
