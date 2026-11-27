"""Security audit event definitions (FCD-05 §17.3)."""

import enum


class SecurityEventType(enum.StrEnum):
    """Standardized event types for security and access audits."""

    USER_REGISTERED = "user.registered"
    LOGIN_SUCCEEDED = "login.succeeded"
    LOGIN_FAILED = "login.failed"
    LOGOUT = "logout"
    LOGOUT_ALL = "logout_all"
    SESSION_CREATED = "session.created"
    SESSION_REVOKED = "session.revoked"
    REFRESH_ROTATED = "refresh.rotated"
    REFRESH_REUSED = "refresh.reused"
    PASSWORD_CHANGED = "password.changed"
    PASSWORD_RESET = "password.reset"
    EMAIL_VERIFIED = "email.verified"
    ACCOUNT_LOCKED = "account.locked"
    ACCOUNT_SUSPENDED = "account.suspended"
    AUTHORIZATION_DENIED = "authorization.denied"
    PLATFORM_ACCESS = "platform.access"
