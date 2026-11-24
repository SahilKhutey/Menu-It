# FCD-05 — Password Recovery & Credential Reset

## 1. Password Reset Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser
    participant API as FastAPI Endpoints
    participant RecovSvc as PasswordRecoveryService
    participant DB as PostgreSQL
    participant SessSvc as SessionService

    User->>API: POST /api/v1/auth/password/forgot {email}
    API->>RecovSvc: create_password_reset_token(email)
    RecovSvc->>DB: Lookup user by normalized_email
    alt User exists & active
        RecovSvc->>DB: Insert PasswordResetToken (H(token), ttl=30m)
        RecovSvc-->>API: raw_token
        API->>User: 200 OK ("If account is eligible, link has been sent.")
    else User not found / suspended
        API->>User: 200 OK (Identical generic response - Anti-Enumeration)
    end

    Note over User,API: User clicks reset link in email
    User->>API: POST /api/v1/auth/password/reset {token, new_password}
    API->>RecovSvc: reset_password(token, new_password)
    RecovSvc->>RecovSvc: Validate password policy
    RecovSvc->>DB: Check token unconsumed and unexpired
    RecovSvc->>DB: Mark token consumed_at = now()
    RecovSvc->>DB: Update UserCredential with new Argon2id hash
    opt User was LOCKED
        RecovSvc->>DB: Set status=ACTIVE, failed_login_attempts=0, locked_until=None
    end
    RecovSvc->>SessSvc: revoke_all_user_sessions(user_id)
    SessSvc->>DB: Revoke all active sessions
    API-->>User: 200 OK ("Password reset successfully.")
```

---

## 2. Security Safeguards

1. **Short Token Lifetime:** Reset tokens expire after 30 minutes (`1800` seconds).
2. **Account Unlock Guarantee:** Resetting password automatically unlocks an account locked by brute-force attempts.
3. **Total Session Revocation:** Upon password reset, all active sessions across all devices are immediately marked `REVOKED`, ensuring a compromised device or active token cannot maintain persistence.
4. **Anti-Enumeration Response:** Submitting an unregistered or inactive email to `/auth/password/forgot` returns HTTP 200 with an identical message, giving an attacker no insight into account existence.
