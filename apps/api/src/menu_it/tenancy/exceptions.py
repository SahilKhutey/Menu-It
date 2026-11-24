"""Tenant resolution exceptions (FCD-04 §9.3)."""


class TenantResolutionError(Exception):
    """Base exception for tenant identification and resolution errors."""

    pass


class TenantNotFoundError(TenantResolutionError):
    """Raised when an organization does not exist or user has no membership."""

    pass


class TenantAccessDeniedError(TenantResolutionError):
    """Raised when user membership is not active (invited, suspended, revoked)."""

    pass


class TenantSuspendedError(TenantResolutionError):
    """Raised when the organization itself is suspended or offboarding."""

    pass


class RestaurantAccessDeniedError(TenantResolutionError):
    """Raised when user lacks required assignment to a requested restaurant."""

    pass


class TenantContextMissingError(TenantResolutionError):
    """Raised when a tenant-scoped operation is invoked without a valid TenantContext."""

    pass
