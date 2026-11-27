# FCD-05 — Acceptance Report & Sign-Off

## 1. Acceptance Criteria Sign-Off Table

| Criterion ID | Requirement | Verification Method | Status |
|---|---|---|:---:|
| **FCD05-AC-01** | User identity model represents person decoupled from organization memberships. | Inspected `User` model; verified in `test_models.py`. | **ACCEPTED** |
| **FCD05-AC-02** | Email normalization applies `strip().casefold()`; duplicate emails rejected. | Verified via `test_email_normalization.py` and registration tests. | **ACCEPTED** |
| **FCD05-AC-03** | Passwords hashed using Argon2id with recommended parameters (64MB, t=3, p=2). | Verified via `test_password_hashing.py`. | **ACCEPTED** |
| **FCD05-AC-04** | Timing attacks mitigated via constant-time dummy verification on absent email. | Verified via `test_password_hashing.py` and `test_login_flow.py`. | **ACCEPTED** |
| **FCD05-AC-05** | Password policy enforces min 12, max 128 chars, no surrounding whitespace or control chars. | Verified via `test_password_policy.py`. | **ACCEPTED** |
| **FCD05-AC-06** | Access tokens issued as short-lived JWTs (10m TTL) containing minimal claims (`sub`, `sid`). | Verified via `test_access_tokens.py`. | **ACCEPTED** |
| **FCD05-AC-07** | Refresh tokens issued as high-entropy opaque strings delivered in HttpOnly cookies. | Verified via `test_auth_endpoints.py` and `test_refresh_rotation.py`. | **ACCEPTED** |
| **FCD05-AC-08** | Automatic refresh token rotation with token family tracking and reuse detection. | Verified via `test_refresh_rotation.py`. | **ACCEPTED** |
| **FCD05-AC-09** | Reused refresh token immediately revokes entire token family and active session. | Verified via `test_refresh_rotation.py`. | **ACCEPTED** |
| **FCD05-AC-10** | Session management supports single-device logout and global all-device logout. | Verified via `test_session_lifecycle.py` and `test_auth_endpoints.py`. | **ACCEPTED** |
| **FCD05-AC-11** | Email verification workflow issues single-use tokens and activates user account. | Verified via `test_email_verification.py`. | **ACCEPTED** |
| **FCD05-AC-12** | Password recovery issues single-use tokens, updates hash, unlocks account, revokes sessions. | Verified via `test_password_recovery.py`. | **ACCEPTED** |
| **FCD05-AC-13** | Account lockout triggered after 5 consecutive failed attempts (15m window). | Verified via `test_authentication_security.py`. | **ACCEPTED** |
| **FCD05-AC-14** | Rate limiter protects login and recovery endpoints against brute-force attacks. | Verified via `test_rate_limiting.py` and `test_authentication_security.py`. | **ACCEPTED** |
| **FCD05-AC-15** | Fine-grained permission catalog defines standard `<resource>:<action>` tokens. | Inspected `Permission(StrEnum)`; verified in `test_role_policies.py`. | **ACCEPTED** |
| **FCD05-AC-16** | Organization and restaurant role-permission matrices enforce principle of least privilege. | Verified via `test_role_policies.py`. | **ACCEPTED** |
| **FCD05-AC-17** | Platform roles maintained in separate table; tenant owners cannot access platform admin. | Verified via `test_platform_boundary.py`. | **ACCEPTED** |
| **FCD05-AC-18** | FCD-04 `TenantResolver` receives `AuthenticatedPrincipal` and resolves tenant context. | Verified via `test_tenant_auth_integration.py`. | **ACCEPTED** |
| **FCD05-AC-19** | Alembic migration `0003_identity_foundation` executes forward and backward cleanly. | Verified via `test_migrations.py`. | **ACCEPTED** |
| **FCD05-AC-20** | Full test suite passes 100% with >= 90% overall code coverage. | 147 tests passed (0 failed), 90% coverage achieved. | **ACCEPTED** |

---

## 2. Conclusion & Sign-Off

All twenty acceptance criteria (**FCD05-AC-01** through **FCD05-AC-20**) are fully satisfied. Phase **FCD-05** is accepted and ready for merging into the baseline.
