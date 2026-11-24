# FCD-05 — Security Controls, Rate Limiting & Audit Logging

## 1. Rate Limiting Architecture

To protect authentication and sensitive recovery endpoints from brute-force password cracking, credential stuffing, and denial-of-service, Menu-It incorporates sliding window rate limiting.

### Endpoint Thresholds

| Endpoint Scope | Max Requests | Time Window | Action on Violation |
|---|---|---|---|
| `POST /auth/login` | 10 requests | 60 seconds (per IP) | HTTP 429 Too Many Requests |
| `POST /auth/register` | 5 requests | 300 seconds (per IP) | HTTP 429 Too Many Requests |
| `POST /auth/password/forgot` | 3 requests | 900 seconds (per email/IP) | HTTP 429 Too Many Requests |
| General API Endpoints | 100 requests | 60 seconds (per user/IP) | HTTP 429 Too Many Requests |

Implementation: [rate_limiting.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/security/rate_limiting.py)

---

## 2. Account Lockout Controls

In addition to network-level rate limiting, Menu-It implements per-account lockout defense:
- **Maximum Consecutive Failures:** 5 failed attempts.
- **Lockout Duration:** 15 minutes (900 seconds).
- **Behavior:** Upon the 5th consecutive failure, `User.status` transitions to `UserStatus.LOCKED`, and `User.locked_until` is set.
- **Bypass Resistance:** While locked, even providing the correct password will return HTTP 423 Locked.
- **Recovery:** Account automatically unlocks when the lockout window elapses, or immediately upon successful completion of the password reset flow.

---

## 3. Security Audit Event Catalog

Defined in [events.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/security/events.py), security audit events capture non-repudiable logs of security-critical actions:
- `AUTH_LOGIN_SUCCESS` / `AUTH_LOGIN_FAILURE`
- `AUTH_ACCOUNT_LOCKED`
- `AUTH_TOKEN_ROTATED` / `AUTH_TOKEN_REUSE_DETECTED`
- `AUTH_SESSION_REVOKED` / `AUTH_SESSION_REVOKED_ALL`
- `AUTH_EMAIL_VERIFIED`
- `AUTH_PASSWORD_RESET_REQUESTED` / `AUTH_PASSWORD_RESET_COMPLETED`
- `AUTH_PASSWORD_CHANGED`
- `AUTH_PLATFORM_ACCESS_GRANTED` / `AUTH_PLATFORM_ACCESS_REVOKED`
