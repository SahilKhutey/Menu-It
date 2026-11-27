# FCD-05 — Token Architecture & Cryptographic Standards

## 1. Access Token Specification (JWT)

Menu-It uses JSON Web Tokens (JWT) for stateless request authorization. Access tokens are short-lived, minimizing the exposure window in case of interception.

### JWT Claims Schema

| Claim | Type | Description | Example |
|---|---|---|---|
| `iss` | `string` | Issuer identifier (configured via `AUTH_ISSUER`) | `"menu-it-auth"` |
| `aud` | `string` | Target audience (configured via `AUTH_AUDIENCE`) | `"menu-it-platform"` |
| `sub` | `UUID` (string) | Authenticated user identity UUID | `"4a87c02b-a01f-442a-a92c-63b7858c5417"` |
| `sid` | `UUID` (string) | Associated active database session UUID | `"7b8e19c3-9821-4fa3-912f-9201824128f4"` |
| `jti` | `UUID` (string) | Unique token identifier (replay mitigation) | `"9d3e811c-d784-4b53-839f-21f4358a901e"` |
| `iat` | `integer` | Epoch timestamp when token was issued | `1716540000` |
| `nbf` | `integer` | Epoch timestamp before which token is invalid | `1716540000` |
| `exp` | `integer` | Epoch timestamp when token expires (TTL: 10 minutes) | `1716540600` |

### Invariant: Minimal Claims Payload
To uphold tenant isolation and strict separation of concerns, the access token **does NOT contain tenant roles, organization IDs, restaurant IDs, or permission lists**. Those authorizations are dynamic and resolved server-side on every request by the FCD-04 `TenantResolver`.

---

## 2. Refresh Token Specification (Opaque)

Unlike access tokens, refresh tokens are **opaque, cryptographically random strings** containing at least 256 bits of entropy:
- Generated via `secrets.token_urlsafe(64)`.
- Never stored in plaintext in the database.
- Stored exclusively as a SHA-256 digest (`hashlib.sha256(raw.encode()).hexdigest()`).
- Delivered to web clients in a secure `HttpOnly`, `SameSite=Lax`, `Secure` cookie scoped strictly to `/api/v1/auth`.

---

## 3. Supported Signature Algorithms

The system supports symmetric (`HS256`) for lightweight local environments and asymmetric (`RS256`, `EdDSA`) for distributed enterprise deployments. Token validation checks verify `iss`, `aud`, expiration, and ensure `none` algorithm attacks are unconditionally rejected.
