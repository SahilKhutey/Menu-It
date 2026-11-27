"""Pure deterministic configuration resolution engine (FCD-15 §2.3, §5)."""

from collections.abc import Sequence

from menu_it.domain.restaurant_configuration.entities import (
    BranchConfigurationEntity,
    EffectiveRestaurantConfiguration,
    RestaurantBrandingEntity,
)
from menu_it.domain.restaurant_configuration.schedule import ScheduleExceptionEntry
from menu_it.domain.restaurant_configuration.value_objects import (
    OpeningInterval,
    OperationalSettings,
    ServiceModeConfig,
    ServiceType,
)


def resolve_service_modes(
    *,
    restaurant_services: dict[str, ServiceModeConfig],
    branch_overrides: dict[str, ServiceModeConfig | None] | None = None,
) -> dict[str, ServiceModeConfig]:
    """Merge restaurant service defaults with explicit branch overrides.

    A missing or None override inherits the restaurant default.
    An explicit override with enabled=False disables the service (no inheritance).
    """
    resolved: dict[str, ServiceModeConfig] = dict(restaurant_services)
    if not branch_overrides:
        return resolved

    for service_key, override_cfg in branch_overrides.items():
        if override_cfg is not None:
            resolved[service_key] = override_cfg
    return resolved


def build_effective_configuration(
    *,
    organization_id,
    restaurant_id,
    restaurant_name: str,
    restaurant_timezone: str,
    organization_currency: str,
    restaurant_phone: str | None = None,
    restaurant_services: dict[str, ServiceModeConfig] | None = None,
    restaurant_weekly_hours: dict[int, tuple[OpeningInterval, ...]] | None = None,
    restaurant_exceptions: Sequence[ScheduleExceptionEntry] = (),
    branding: RestaurantBrandingEntity | None = None,
    restaurant_operational_settings: OperationalSettings | None = None,
    branch_id=None,
    branch_timezone: str | None = None,
    branch_phone: str | None = None,
    branch_config: BranchConfigurationEntity | None = None,
    revision: int = 1,
) -> EffectiveRestaurantConfiguration:
    """Resolve effective restaurant or branch configuration deterministically."""
    base_services = dict(restaurant_services or {})
    if not base_services:
        base_services = {
            ServiceType.DINE_IN.value: ServiceModeConfig(
                service_type=ServiceType.DINE_IN, enabled=True
            )
        }

    base_hours = dict(restaurant_weekly_hours or {})
    base_exceptions = tuple(restaurant_exceptions)
    base_ops = restaurant_operational_settings or OperationalSettings()

    effective_name = restaurant_name
    effective_tz = branch_timezone or restaurant_timezone or "UTC"
    effective_phone = branch_phone if branch_phone is not None else restaurant_phone
    effective_services = base_services
    effective_hours = base_hours
    effective_exceptions = base_exceptions
    effective_ops = base_ops

    if branch_config is not None:
        if branch_config.display_name_override is not None:
            effective_name = branch_config.display_name_override
        if branch_config.public_phone_override is not None:
            effective_phone = branch_config.public_phone_override
        if branch_config.service_override_enabled:
            effective_services = resolve_service_modes(
                restaurant_services=base_services,
                branch_overrides=branch_config.service_overrides,
            )
        if branch_config.schedule_override_enabled:
            if branch_config.weekly_hours_override:
                effective_hours = dict(branch_config.weekly_hours_override)
            if branch_config.schedule_exceptions_override:
                effective_exceptions = branch_config.schedule_exceptions_override
        if branch_config.operational_settings_override is not None:
            effective_ops = branch_config.operational_settings_override

    enabled_services = tuple(sorted(key for key, cfg in effective_services.items() if cfg.enabled))

    return EffectiveRestaurantConfiguration(
        organization_id=organization_id,
        restaurant_id=restaurant_id,
        branch_id=branch_id,
        display_name=effective_name,
        timezone=effective_tz,
        currency_code=organization_currency,
        public_phone=effective_phone,
        enabled_services=enabled_services,
        services=effective_services,
        weekly_hours=effective_hours,
        schedule_exceptions=effective_exceptions,
        branding=branding,
        operational_settings=effective_ops,
        revision=revision,
    )
