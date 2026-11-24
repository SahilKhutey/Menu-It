"""Session domain exceptions (FCD-05 §9.3)."""


class SessionError(Exception):
    """Base exception for session-related errors."""


class SessionNotFoundError(SessionError):
    """Raised when the requested session does not exist."""


class SessionRevokedError(SessionError):
    """Raised when attempting to operate on a revoked session."""


class SessionExpiredError(SessionError):
    """Raised when session duration has expired."""


class InvalidRefreshTokenError(SessionError):
    """Raised when provided refresh token is invalid or expired."""


class TokenReuseDetectedError(SessionError):
    """Raised when an already-consumed refresh token is presented, indicating potential theft."""
