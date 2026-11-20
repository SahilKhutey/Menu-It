# MOD-01 — Identity & Authentication Module Specification

**Module ID:** MOD-01  
**Tier:** Platform Foundation (P0)  
**Package:** `app.modules.identity`  

---

## 1. Ownership & Boundaries
- **Owns:** User accounts, credentials, password hashes, authentication sessions, verification tokens.
- **Does Not Own:** Organization memberships, restaurant roles, subscription entitlements.

## 2. Domain Model & Invariants
- **User Entity:** `User(id, email, password_hash, is_active, is_verified)`
  - Normalized email via `EmailAddress`. Max 254 chars, regex validated.
  - Inactive accounts cannot authenticate (`assert_can_authenticate()`).
- **Session Entity:** `Session(id, user_id, is_revoked)`
  - Revoked sessions fail validity check (`assert_valid()`).

## 3. Public Contracts & Events
- **Provides:** `IdentityVerifier` Protocol (`verify_user_active(user_id)`).
- **Emits:** `UserRegistered` (EVT-001).
