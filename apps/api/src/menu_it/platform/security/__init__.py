"""Security assurance and boundary enforcement package (FCD-11)."""

from menu_it.platform.security.authorization import (
    PermissionDeniedError,
    TenantAccessDeniedError,
    assert_tenant_boundary,
    require_permission,
)
from menu_it.platform.security.config_validation import (
    SecurityConfigurationError,
    SecurityConfigValidator,
    ensure_production_config,
    validate_production_config,
)
from menu_it.platform.security.rate_limit import (
    InMemoryRateLimiter,
    RateLimiter,
    RateLimitExceededException,
    RateLimitResult,
    RedisRateLimiter,
)

__all__ = [
    "InMemoryRateLimiter",
    "PermissionDeniedError",
    "RateLimitExceededException",
    "RateLimitResult",
    "RateLimiter",
    "RedisRateLimiter",
    "SecurityConfigValidator",
    "SecurityConfigurationError",
    "TenantAccessDeniedError",
    "assert_tenant_boundary",
    "ensure_production_config",
    "require_permission",
    "validate_production_config",
]
