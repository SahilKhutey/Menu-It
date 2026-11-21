# 07. Authentication Architecture

## 1. Dual Authentication Model
- **First-Party Web Application:** `HttpOnly`, `SameSite=Lax`, `Secure` session cookies (`modularmenu_session`). Protects against XSS token exfiltration.
- **API Consumers & Automations:** `Authorization: Bearer <JWT>` signed with HMAC-SHA256.

## 2. Session Lifecycle
- Login issues session cookie and returns user profile.
- Logout revokes session server-side and clears cookies with `Max-Age=0`.
