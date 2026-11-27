"""FCD-15 Restaurant Profile, Branding & Operational Configuration domain package."""

from menu_it.domain.restaurant_configuration.entities import (
    BranchConfigurationEntity,
    EffectiveRestaurantConfiguration,
    PublicProfilePublicationEntity,
    RestaurantBrandingEntity,
)
from menu_it.domain.restaurant_configuration.resolver import (
    build_effective_configuration,
    resolve_service_modes,
)
from menu_it.domain.restaurant_configuration.schedule import (
    OpenStatusResult,
    ScheduleExceptionEntry,
    evaluate_open_status,
    validate_daily_intervals,
)
from menu_it.domain.restaurant_configuration.value_objects import (
    ExceptionType,
    HexColor,
    OpeningInterval,
    OperationalSettings,
    PublicationStatus,
    ServiceModeConfig,
    ServiceType,
)

__all__ = [
    "BranchConfigurationEntity",
    "EffectiveRestaurantConfiguration",
    "ExceptionType",
    "HexColor",
    "OpenStatusResult",
    "OpeningInterval",
    "OperationalSettings",
    "PublicProfilePublicationEntity",
    "PublicationStatus",
    "RestaurantBrandingEntity",
    "ScheduleExceptionEntry",
    "ServiceModeConfig",
    "ServiceType",
    "build_effective_configuration",
    "evaluate_open_status",
    "resolve_service_modes",
    "validate_daily_intervals",
]
