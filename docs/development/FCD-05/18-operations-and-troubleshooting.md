# FCD-05 — Operations & Troubleshooting Guide

## 1. Operational Configuration Reference

All authentication parameters are configurable via environment variables in `apps/api/src/menu_it/core/config.py`:

| Environment Variable | Default Value | Description |
|---|---|---|
| `AUTH_SECRET_KEY` | *(Validated)* | Cryptographic key used to sign and verify JWT access tokens |
| `AUTH_JWT_ALGORITHM` | `"HS256"` | JWT algorithm (`HS256`, `RS256`, `EdDSA`) |
| `AUTH_ACCESS_TOKEN_TTL_SECONDS` | `600` | Lifetime of access tokens (10 minutes) |
| `AUTH_REFRESH_TOKEN_TTL_SECONDS`| `2592000` | Lifetime of refresh tokens (30 days) |
| `AUTH_MAX_FAILED_LOGINS` | `5` | Maximum failed attempts before temporary account lockout |
| `AUTH_LOCKOUT_SECONDS` | `900` | Account lockout duration (15 minutes) |
| `AUTH_PASSWORD_RESET_TTL_SECONDS`| `1800` | Lifetime of password recovery tokens (30 minutes) |
| `AUTH_EMAIL_VERIFICATION_TTL_SECONDS` | `86400` | Lifetime of email verification tokens (24 hours) |
| `AUTH_COOKIE_SECURE` | `True` | Requires HTTPS for refresh token cookie in production |
| `AUTH_COOKIE_SAMESITE` | `"lax"` | Cookie SameSite policy |

---

## 2. Common Operational Issues & Troubleshooting

### Issue: Client Receives 401 Unauthorized with "Access token has expired"
- **Cause:** Access token exceeded its 10-minute lifetime.
- **Remedy:** Client should intercept 401, call `POST /api/v1/auth/refresh` using its refresh cookie to obtain a new access token, and replay the original request.

### Issue: Client Receives 423 Locked with "Account is temporarily locked"
- **Cause:** 5 consecutive incorrect passwords were submitted within the lockout window.
- **Remedy:** User must either wait 15 minutes for the lockout window to elapse or initiate a password reset via `POST /api/v1/auth/password/forgot`.

### Issue: Token Reuse Detected Error (All devices logged out)
- **Cause:** A refresh token that had already been consumed was submitted again. This typically indicates network token replay, client race condition, or a compromised refresh token being presented by an attacker.
- **Action:** Inform user of security precaution; user must re-authenticate with primary credentials.
