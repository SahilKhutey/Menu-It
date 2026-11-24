# FCD-05 — Database Schema Migrations

## 1. Migration Overview

Phase FCD-05 introduces migration revision `0003_create_identity_and_auth_foundation.py` (`0003_identity_foundation`).

- **Previous Revision:** `0002_multi_tenant_foundation`
- **Current Revision:** `0003_identity_foundation`
- **File:** [0003_create_identity_and_auth_foundation.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/alembic/versions/0003_create_identity_and_auth_foundation.py)

---

## 2. Created Database Entities

The migration provisions six new relational tables and reinforces foreign key integrity across organization memberships:

1. **`users`:** Primary user identity accounts with unique constraint on `normalized_email`.
2. **`user_credentials`:** Argon2id password hash records cascading on user deletion (`ondelete="CASCADE"`).
3. **`user_sessions`:** Active sessions tracking client metadata, last activity, expiration, and status.
4. **`refresh_tokens`:** Hashed refresh token records tied to a token family (`family_id`) for rotation and reuse detection.
5. **`email_verification_tokens`:** Hashed single-use tokens for activating user accounts.
6. **`password_reset_tokens`:** Hashed single-use tokens for password recovery.
7. **`platform_memberships`:** Global SaaS administrative roles separate from tenant organizations.

### Foreign Key Backfill & Cascade Safety
The migration reconciles `organization_memberships(user_id)` and `restaurant_memberships(user_id)`:
- Backfills missing mock users from existing memberships so foreign key constraints apply cleanly.
- Adds foreign key constraint referencing `users.id` with `ondelete="CASCADE"`.

---

## 3. Migration Lifecycle Verification

The migration was thoroughly verified with automated bidirectional test `test_alembic_migration_lifecycle`:
```bash
0001 -> 0002 -> 0003 -> 0002 -> 0001 -> base -> head
```
All forward upgrades and downward downgrades complete with zero errors.
