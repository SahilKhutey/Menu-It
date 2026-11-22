"""
ModularMenu — Tenant Domain Exceptions (ARC-05 §5.5, §15.1).
Strict security and isolation exceptions mapping to RFC 7807 problem responses.
"""


class TenantSecurityException(Exception):
    """Base exception for all tenancy-related security violations."""

    pass


class TenantAccessDeniedException(TenantSecurityException):
    """Raised when an authenticated identity lacks required tenant or branch permissions."""

    def __init__(self, message: str = "Access denied for tenant resource"):
        super().__init__(message)


class CrossTenantAccessException(TenantSecurityException):
    """Raised when an operation attempts to read, write, or forge access across tenant boundaries."""

    def __init__(self, message: str = "Cross-tenant access attempt strictly prohibited"):
        super().__init__(message)


class InvalidTenantContextException(TenantSecurityException):
    """Raised when an operation executes with a missing, corrupted, or unvalidated tenant context."""

    def __init__(self, message: str = "Invalid or unverified tenant context"):
        super().__init__(message)


class TenantSuspendedException(TenantSecurityException):
    """Raised when access is attempted against an organization currently in suspended state."""

    def __init__(self, message: str = "Organization account is suspended"):
        super().__init__(message)


class TenantResourceNotFoundException(TenantSecurityException):
    """Raised when a resource does not exist within the caller's authorized tenant scope."""

    def __init__(self, message: str = "Resource not found within tenant scope"):
        super().__init__(message)


class TenantRelationalIntegrityException(TenantSecurityException):
    """Raised when attempting to associate a child resource with a parent from another tenant."""

    def __init__(self, message: str = "Cross-tenant foreign relationship creation prohibited"):
        super().__init__(message)
