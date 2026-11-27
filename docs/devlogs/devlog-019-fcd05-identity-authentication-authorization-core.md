# Devlog 019 — FCD-05 Identity, Authentication & Authorization Core

**Date:** 2026-11-24  
**Author:** AI Architecture & Core Engineering Team  
**Subject:** Implementation, Verification, and Release of FCD-05 Identity, Authentication & Authorization Core  
**Milestone:** `v1.0.0-fcd05`  
**Phase:** Foundational Core Development (FCD-05)  
**Parent Documents:** FCD-01, FCD-02, FCD-03, FCD-04, ARC-01 through ARC-12  

---

## 1. Objectives & Context

Phase **FCD-05** builds the identity, credential, authentication, session, verification, recovery, permission, and access-control infrastructure for the **Menu-It** multi-tenant SaaS platform.

It builds directly upon the organization-centric multi-tenant foundation established in **FCD-04**, separating identity, authentication, session lifecycle, tenant access, and fine-grained authorization:
1. **Decoupled User Identity (`users`):** Independent person accounts tracking lifecycle states (`PENDING_VERIFICATION`, `ACTIVE`, `LOCKED`, `SUSPENDED`, `DEACTIVATED`) and verified emails, entirely distinct from organization memberships.
2. **Canonical Email Normalization:** Strict `strip().casefold()` normalization preventing account collisions and duplicate registration attacks.
3. **Argon2id Credential Security (`user_credentials`):** Industry-standard password hashing (64MB memory, 3 iterations, 2 parallelism lanes) with constant-time dummy verification mitigating timing-based account enumeration.
4. **NIST SP 800-63B Password Policy:** Enforcing 12–128 characters, disallowing surrounding whitespace and control characters.
5. **Cryptographic Token Architecture:**
   - **Access Tokens:** Short-lived JWTs (10-minute TTL) containing minimal claims (`sub`, `sid`, `jti`) signed with secret key, strictly decoupled from tenant claims.
   - **Refresh Tokens:** High-entropy opaque strings (64-byte URL-safe) stored exclusively as SHA-256 digests, delivered in secure `HttpOnly`, `SameSite=Lax`, `Secure` cookies.
6. **Session Management & Refresh Rotation:**
   - Automatic refresh token rotation with token family tracking (`family_id`).
   - Pessimistic row locking (`SELECT ... FOR UPDATE`) during rotation.
   - Immediate reuse detection automatically revoking the entire token family and terminating the active session upon replay.
   - Device session tracking (`UserSession`), single-device logout, and global all-device logout.
7. **Email Verification & Account Activation:** Single-use SHA-256 hashed verification tokens activating unverified accounts.
8. **Password Recovery Workflow:** Self-service password reset tokens (30-minute TTL) resetting credential hashes, unlocking locked accounts, and terminating all active sessions across devices.
9. **Fine-Grained Authorization & Role-Permission Matrix:**
   - Standardized `<resource>:<action>` permission tokens (`Permission` StrEnum).
   - Organization role mappings (`OWNER`, `ADMIN`, `MANAGER`, `STAFF`, `VIEWER`).
   - Restaurant role mappings (`RESTAURANT_MANAGER`, `KITCHEN_STAFF`, `SERVICE_STAFF`).
   - Pure policy evaluation engine and declarative FastAPI dependency `require_permission(Permission)`.
10. **Platform Privilege Separation (`platform_memberships`):**
    - Isolated global SaaS administrative privileges (`platform_admin`, `platform_support`, `platform_operator`).
    - Mutual exclusivity: tenant owners possess zero platform authority; platform admin endpoints gated via `require_platform_role`.
11. **Tenant-Auth Integration:**
    - `get_current_principal` decodes JWT, validates active database session, and passes `AuthenticatedPrincipal` to FCD-04 `TenantResolver`.
    - Added `/api/v1/organizations/{organization_id}/access` endpoint returning verified tenant permissions.
12. **Security Controls & Rate Limiting:**
    - Sliding window in-memory rate limiting on login, registration, and recovery endpoints.
    - Automatic account lockout after 5 consecutive failed attempts (15-minute window).
    - Structured security audit event emission (`SecurityEventType`).
13. **Database Migration & Verification:**
    - Alembic revision `0003_identity_foundation` (`0003_create_identity_and_auth_foundation.py`).
    - 147 automated unit, integration, and security tests passing 100% with 90% overall code coverage.
    - 21 comprehensive technical documents authored in `docs/development/FCD-05/`.

---

## 2. Key Engineering Accomplishments

### 2.1 Database Models & ORM Layer (WP-01, WP-02)
- Created `apps/api/src/menu_it/database/models/user.py` (`User`, `UserStatus`, `normalize_email`).
- Created `apps/api/src/menu_it/database/models/credential.py` (`UserCredential` with cascade on `users.id`).
- Created `apps/api/src/menu_it/database/models/session.py` (`UserSession`, `SessionStatus`, `RefreshTokenRecord`).
- Created `apps/api/src/menu_it/database/models/verification.py` (`EmailVerificationToken`).
- Created `apps/api/src/menu_it/database/models/recovery.py` (`PasswordResetToken`).
- Created `apps/api/src/menu_it/database/models/platform.py` (`PlatformMembership`, `PlatformRole`, `PlatformMembershipStatus`).
- Updated `OrganizationMembership` and `RestaurantMembership` with foreign key referencing `users.id` on delete cascade.
- Exported all models in `apps/api/src/menu_it/database/models/__init__.py`.

### 2.2 Credentials, Tokens & Sessions (WP-03 – WP-06)
- Implemented Argon2id password hasher with timing dummy work in `menu_it.credentials.hashing`.
- Implemented NIST-compliant password validation in `menu_it.credentials.password_policy`.
- Implemented JWT issuance, decoding, and opaque token hashing in `menu_it.authentication.tokens`.
- Implemented `SessionRepository` and `SessionService` in `menu_it.sessions` with atomic token family rotation, pessimistic row locking, and automatic reuse detection.
- Implemented `EmailVerificationService` in `menu_it.verification`.
- Implemented `PasswordRecoveryService` in `menu_it.recovery`.

### 2.3 Authentication, Authorization & Dependencies (WP-07 – WP-10)
- Implemented `AuthenticationService` in `menu_it.authentication.service` coordinating registration, login, lockout tracking, token rotation, and password changes.
- Updated `AuthenticatedPrincipal(user_id, session_id, is_authenticated)` in `menu_it.auth.principal`.
- Updated `get_current_principal` dependency in `menu_it.auth.dependencies` validating JWT signatures, active database sessions, and active user account state.
- Implemented permission catalog, role matrices, policy evaluators, and `require_permission` / `require_platform_role` dependencies in `menu_it.authorization`.

### 2.4 API Endpoints (WP-11 – WP-13)
- Implemented `/api/v1/auth` endpoints (`/register`, `/login`, `/refresh`, `/logout`, `/logout-all`, `/email/verify`, `/email/resend`, `/password/forgot`, `/password/reset`, `/password/change`) in `apps/api/src/menu_it/api/v1/endpoints/auth.py`.
- Implemented `/api/v1/identity/me` profile endpoints in `apps/api/src/menu_it/api/v1/endpoints/identity.py`.
- Implemented `/api/v1/sessions` device management endpoints in `apps/api/src/menu_it/api/v1/endpoints/sessions.py`.
- Added `/api/v1/organizations/{organization_id}/access` endpoint in `apps/api/src/menu_it/api/v1/endpoints/organizations.py`.
- Registered all routers in `apps/api/src/menu_it/api/v1/router.py`.

### 2.5 Alembic Migration & Test Suites (WP-14 – WP-16)
- Authored revision `0003_create_identity_and_auth_foundation.py` provisioning all FCD-05 tables and foreign key constraints.
- Authored comprehensive test suites:
  - `apps/api/tests/unit/credentials/` (hashing, password policy)
  - `apps/api/tests/unit/authentication/` (access tokens)
  - `apps/api/tests/unit/authorization/` (role policies)
  - `apps/api/tests/unit/identity/` (email normalization)
  - `apps/api/tests/unit/security/` (rate limiting)
  - `apps/api/tests/integration/` (registration, login, session lifecycle, refresh rotation, email verification, password recovery, tenant auth integration)
  - `apps/api/tests/security/` (authentication security, platform boundary)
  - `apps/api/tests/api/` (auth endpoints, identity and session endpoints)
- Total test count: 147 passed (0 failed). Overall code coverage: 90%.

---

## 3. Verification & Acceptance Summary

All 20 acceptance criteria (**FCD05-AC-01** through **FCD05-AC-20**) are satisfied:
- Hashing: Argon2id with 64MB memory hardness verified.
- Timing attack mitigation: Dummy hash work verified.
- Token rotation & reuse detection: Token family revocation upon replay attack verified.
- Session lifecycle: Single-device and global logout verified.
- Email verification & password recovery: One-time token consumption verified.
- Privilege separation: Platform admin boundary verified.
- Multi-tenant integration: Bearer JWT tenant resolution verified.
- Quality gates: 0 Ruff lint errors, 0 format violations, 0 TypeScript errors.
