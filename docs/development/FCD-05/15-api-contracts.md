# FCD-05 — Authentication & Identity API Contracts

## 1. Authentication Endpoints Overview

All authentication endpoints reside under the `/api/v1/auth` prefix and return standardized `APIResponse[T]` payloads.

### Endpoint Route Matrix

| Method | Route | Description | Auth Required |
|---|---|---|:---:|
| `POST` | `/api/v1/auth/register` | Self-service account registration | No |
| `POST` | `/api/v1/auth/login` | Email/password login with JWT & refresh cookie | No |
| `POST` | `/api/v1/auth/refresh` | Rotate refresh token and issue new JWT | Cookie / Body |
| `POST` | `/api/v1/auth/logout` | Revoke current active session | Bearer JWT |
| `POST` | `/api/v1/auth/logout-all` | Revoke all sessions across all devices | Bearer JWT |
| `POST` | `/api/v1/auth/email/verify` | Verify email token and activate account | No |
| `POST` | `/api/v1/auth/email/resend` | Request new email verification link | No |
| `POST` | `/api/v1/auth/password/forgot` | Initiate password recovery workflow | No |
| `POST` | `/api/v1/auth/password/reset` | Complete password reset with token | No |
| `POST` | `/api/v1/auth/password/change` | Change password with current password verification | Bearer JWT |
| `GET` | `/api/v1/identity/me` | Fetch authenticated user profile | Bearer JWT |
| `PATCH` | `/api/v1/identity/me` | Update authenticated user profile | Bearer JWT |
| `GET` | `/api/v1/sessions` | List active device sessions for current user | Bearer JWT |
| `DELETE` | `/api/v1/sessions/{id}` | Revoke a specific device session | Bearer JWT |
| `GET` | `/api/v1/organizations/{id}/access` | Retrieve verified permissions for tenant | Bearer JWT |

---

## 2. Request & Response Payload Examples

### Login Request (`POST /api/v1/auth/login`)
```json
{
  "email": "owner@acmerestaurants.com",
  "password": "CorrectPassword123!@"
}
```

### Login Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 600,
    "user": {
      "id": "c1f7a28e-8a21-4c19-b003-8e92f038c114",
      "email": "owner@acmerestaurants.com",
      "display_name": "Jane Owner",
      "status": "active",
      "email_verified": true,
      "created_at": "2026-11-24T08:00:00Z",
      "updated_at": "2026-11-24T08:00:00Z"
    },
    "refresh_token": "u4Z8...random-token-string"
  },
  "error": null,
  "meta": {
    "request_id": "9d3e811c-d784-4b53-839f-21f4358a901e",
    "timestamp": "2026-11-24T08:00:01Z"
  }
}
```
*HTTP Header:*
`Set-Cookie: menu_it_refresh=u4Z8...; Path=/api/v1/auth; HttpOnly; SameSite=Lax; Max-Age=2592000`
