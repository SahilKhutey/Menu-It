"""
ModularMenu — Security Engineering Package (ARC-12).
"""

from app.security.audit import AuditEvent, AuditLogger, audit_logger
from app.security.authorization import (
    ROLE_PERMISSIONS,
    AuthorizationContext,
    require_permission,
    require_restaurant_access,
)
from app.security.passwords import hash_password, needs_rehash, verify_password
from app.security.sessions import SessionStore, UserSession, session_store
from app.security.webhooks import (
    WebhookReplayGuard,
    default_webhook_guard,
    verify_webhook_signature,
)

__all__ = [
    "AuditEvent",
    "AuditLogger",
    "audit_logger",
    "ROLE_PERMISSIONS",
    "AuthorizationContext",
    "require_permission",
    "require_restaurant_access",
    "hash_password",
    "verify_password",
    "needs_rehash",
    "UserSession",
    "SessionStore",
    "session_store",
    "verify_webhook_signature",
    "WebhookReplayGuard",
    "default_webhook_guard",
]
