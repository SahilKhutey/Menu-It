# ARC-02 Security Architecture Review

**Document ID:** REP-ARC02-03  
**Review Type:** Architecture Security Baseline & Tenant Isolation Audit  
**Date:** 2026-11-19  
**Reviewer:** Lead Architect & Security Lead  
**Status:** Approved

---

## 1. Threat Modeling & Security Posture

ModularMenu operates in a hybrid delivery environment. We evaluated the architecture against the following critical risk vectors:

### 1.1 Multi-Tenant Data Leakage (OWASP A01: Broken Access Control)
- **Defensive Mechanism:**
  1. Ingress JWT middleware resolves user ID and verifies signature with HS256.
  2. Dependency `get_current_restaurant_membership` verifies that the caller has an active `RestaurantMember` role for the targeted restaurant before allowing any action.
  3. Every database query in tenant modules (`menus`, `categories`, `menu_items`, `themes`) explicitly qualifies queries with `restaurant_id`.
  4. PostgreSQL Row-Level Security (RLS) is architectural baseline for the multi-tenant database.
- **Audit Result:** Automated test `test_cross_tenant_isolation_strictly_enforced` confirms that Tenant A receives `403 Forbidden` on every attempt to read, create, or modify Tenant B data.

### 1.2 Cryptographic Token Integrity
- **Defensive Mechanism:** JWT tokens signed with SHA-256 HMAC; subject contains UUIDv4 user ID.
- **Audit Result:** Tampered or forged signatures return `401 Unauthorized` (`test_tampered_token_rejected`).

### 1.3 Public Endpoint Enumeration & Data Poisoning
- **Defensive Mechanism:**
  1. Public customer menu path (`/api/v1/public/restaurants/{slug}/menu`) accesses only frozen snapshots in `menu_versions`.
  2. Mutable draft data in `menus` and `menu_items` is never exposed or queried on the public diner route.
  3. Unpublished draft changes remain invisible to public diners until an authorized operator triggers the `/publish` endpoint.
- **Audit Result:** Verified in `test_publishing_creates_immutable_snapshot_and_serves_publicly`.

### 1.4 Code Injection & XSS via Theme Customizations
- **Defensive Mechanism:**
  1. Themes are constrained to structured JSON tokens (colors, typography, layout).
  2. Hex colors are strictly validated against `^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$`.
  3. Custom user JavaScript or CSS upload is architecturally prohibited (Principle P-03, P-10).
- **Audit Result:** Verified in `test_hex_color_validation`.

---

## 2. Security Sign-Off

The system satisfies all security constraints set forth in ARC-02 §10 WP-ARC02-06.
