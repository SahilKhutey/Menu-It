"""FCD-15 Restaurant & Branch configuration application service."""

from collections.abc import Sequence
from datetime import UTC, date, datetime, time
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.branch import Branch
from menu_it.database.models.organization import Organization
from menu_it.database.models.restaurant import Restaurant
from menu_it.database.models.restaurant_configuration import (
    BranchConfiguration,
    BranchServiceConfiguration,
    BranchWeeklyHour,
    RestaurantBranding,
    RestaurantOperationalSetting,
    RestaurantScheduleException,
    RestaurantServiceConfiguration,
    RestaurantWeeklyHour,
)
from menu_it.database.models.restaurant_profile import RestaurantProfileRecord
from menu_it.domain.base.errors import (
    ConcurrencyConflictError,
    EntityNotFoundError,
    ValidationDomainError,
)
from menu_it.domain.restaurant_configuration import (
    BranchConfigurationEntity,
    EffectiveRestaurantConfiguration,
    ExceptionType,
    HexColor,
    OpeningInterval,
    OpenStatusResult,
    OperationalSettings,
    RestaurantBrandingEntity,
    ScheduleExceptionEntry,
    ServiceModeConfig,
    ServiceType,
    build_effective_configuration,
    evaluate_open_status,
    validate_daily_intervals,
)
from menu_it.platform.cache.service import CacheService
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.publisher import OutboxEventPublisher


def _parse_time(val: time | str) -> time:
    if isinstance(val, time):
        return val
    return time.fromisoformat(val)


class RestaurantConfigurationService:
    """Centralized application service for FCD-15 restaurant and branch configuration."""

    def __init__(self, session: AsyncSession, cache: CacheService | None = None) -> None:
        self.session = session
        self.cache = cache
        self.outbox = OutboxEventPublisher(session)

    async def _require_restaurant(
        self, organization_id: UUID, restaurant_id: UUID
    ) -> tuple[Organization, Restaurant]:
        org_res = await self.session.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        org = org_res.scalar_one_or_none()
        if org is None:
            raise EntityNotFoundError(f"Organization '{organization_id}' not found.")

        rest_res = await self.session.execute(
            select(Restaurant).where(
                Restaurant.organization_id == organization_id,
                Restaurant.id == restaurant_id,
            )
        )
        rest = rest_res.scalar_one_or_none()
        if rest is None:
            raise EntityNotFoundError(
                f"Restaurant '{restaurant_id}' not found in organization '{organization_id}'."
            )
        return org, rest

    async def _require_branch(
        self, organization_id: UUID, restaurant_id: UUID, branch_id: UUID
    ) -> Branch:
        res = await self.session.execute(
            select(Branch).where(
                Branch.organization_id == organization_id,
                Branch.restaurant_id == restaurant_id,
                Branch.id == branch_id,
            )
        )
        branch = res.scalar_one_or_none()
        if branch is None:
            raise EntityNotFoundError(
                f"Branch '{branch_id}' not found for restaurant '{restaurant_id}'."
            )
        return branch

    async def _record_event_and_audit(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        event_type: str,
        resource_type: str,
        resource_id: UUID,
        payload: dict[str, Any],
        correlation_id: str | None = None,
    ) -> None:
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type=event_type,
                schema_version=1,
                occurred_at=datetime.now(UTC),
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload=payload,
            )
        )
        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=actor_user_id,
                action=event_type,
                resource_type=resource_type,
                resource_id=str(resource_id),
                correlation_id=correlation_id,
                metadata_=payload,
            )
        )
        if self.cache is not None:
            await self.cache.invalidate_organization_resource(organization_id, "restaurant_config")

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------
    async def get_profile(
        self, organization_id: UUID, restaurant_id: UUID
    ) -> RestaurantProfileRecord:
        _, rest = await self._require_restaurant(organization_id, restaurant_id)
        res = await self.session.execute(
            select(RestaurantProfileRecord).where(
                RestaurantProfileRecord.organization_id == organization_id,
                RestaurantProfileRecord.restaurant_id == restaurant_id,
            )
        )
        record = res.scalar_one_or_none()
        if record is None:
            record = RestaurantProfileRecord(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                public_name=rest.name,
                description=rest.description,
                email=rest.email,
                phone=rest.phone,
                website_url=rest.website,
                cuisine_type=rest.cuisine_type,
                timezone=rest.timezone,
            )
            self.session.add(record)
            await self.session.flush()
        return record

    async def update_profile(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        display_name: str | None = None,
        short_description: str | None = None,
        description: str | None = None,
        cuisine_type: str | None = None,
        price_range: str | None = None,
        website_url: str | None = None,
        public_email: str | None = None,
        public_phone: str | None = None,
        social_links: dict[str, Any] | None = None,
        expected_version: int | None = None,
        correlation_id: str | None = None,
    ) -> RestaurantProfileRecord:
        record = await self.get_profile(organization_id, restaurant_id)
        if expected_version is not None and record.version != expected_version:
            raise ConcurrencyConflictError(
                f"Profile version conflict: expected {expected_version}, "
                f"current is {record.version}."
            )

        if display_name is not None:
            cleaned = display_name.strip()
            if len(cleaned) < 2:
                raise ValidationDomainError("display_name must be at least 2 characters.")
            record.public_name = cleaned
        if short_description is not None:
            record.short_description = short_description
        if description is not None:
            record.description = description
        if cuisine_type is not None:
            record.cuisine_type = cuisine_type
        if price_range is not None:
            record.price_range = price_range
        if website_url is not None:
            record.website_url = website_url
        if public_email is not None:
            record.public_email = public_email
        if public_phone is not None:
            record.public_phone = public_phone
        if social_links is not None:
            record.social_links = dict(social_links)

        record.version += 1
        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.profile.updated",
            resource_type="restaurant_profile",
            resource_id=restaurant_id,
            payload={"restaurant_id": str(restaurant_id), "version": record.version},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return record

    # ------------------------------------------------------------------
    # Branding
    # ------------------------------------------------------------------
    async def get_branding(self, organization_id: UUID, restaurant_id: UUID) -> RestaurantBranding:
        await self._require_restaurant(organization_id, restaurant_id)
        res = await self.session.execute(
            select(RestaurantBranding).where(
                RestaurantBranding.organization_id == organization_id,
                RestaurantBranding.restaurant_id == restaurant_id,
            )
        )
        branding = res.scalar_one_or_none()
        if branding is None:
            branding = RestaurantBranding(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
            )
            self.session.add(branding)
            await self.session.flush()
        return branding

    async def update_branding(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        logo_asset_id: UUID | None = None,
        alternate_logo_asset_id: UUID | None = None,
        cover_asset_id: UUID | None = None,
        favicon_asset_id: UUID | None = None,
        primary_color: str | None = None,
        secondary_color: str | None = None,
        accent_color: str | None = None,
        background_color: str | None = None,
        text_color: str | None = None,
        font_family: str | None = None,
        border_radius: str | None = None,
        theme_preset: str | None = None,
        theme_settings: dict[str, Any] | None = None,
        expected_revision: int | None = None,
        correlation_id: str | None = None,
    ) -> RestaurantBranding:
        branding = await self.get_branding(organization_id, restaurant_id)
        if expected_revision is not None and branding.revision != expected_revision:
            raise ConcurrencyConflictError(
                f"Branding revision conflict: expected {expected_revision}, "
                f"current is {branding.revision}."
            )

        for field_name, color_val in (
            ("primary_color", primary_color),
            ("secondary_color", secondary_color),
            ("accent_color", accent_color),
            ("background_color", background_color),
            ("text_color", text_color),
        ):
            if color_val is not None:
                setattr(branding, field_name, HexColor(color_val).normalized())

        if logo_asset_id is not None:
            branding.logo_asset_id = logo_asset_id
        if alternate_logo_asset_id is not None:
            branding.alternate_logo_asset_id = alternate_logo_asset_id
        if cover_asset_id is not None:
            branding.cover_asset_id = cover_asset_id
        if favicon_asset_id is not None:
            branding.favicon_asset_id = favicon_asset_id
        if font_family is not None:
            branding.font_family = font_family
        if border_radius is not None:
            branding.border_radius = border_radius
        if theme_preset is not None:
            branding.theme_preset = theme_preset
        if theme_settings is not None:
            branding.theme_settings = dict(theme_settings)

        branding.revision += 1
        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.branding.updated",
            resource_type="restaurant_branding",
            resource_id=restaurant_id,
            payload={"restaurant_id": str(restaurant_id), "revision": branding.revision},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return branding

    # ------------------------------------------------------------------
    # Weekly Hours & Schedule Exceptions
    # ------------------------------------------------------------------
    async def get_weekly_hours(
        self, organization_id: UUID, restaurant_id: UUID
    ) -> list[RestaurantWeeklyHour]:
        await self._require_restaurant(organization_id, restaurant_id)
        res = await self.session.execute(
            select(RestaurantWeeklyHour)
            .where(
                RestaurantWeeklyHour.organization_id == organization_id,
                RestaurantWeeklyHour.restaurant_id == restaurant_id,
            )
            .order_by(RestaurantWeeklyHour.day_of_week, RestaurantWeeklyHour.opens_at)
        )
        return list(res.scalars().all())

    async def replace_weekly_hours(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        days: Sequence[dict[str, Any]],
        correlation_id: str | None = None,
    ) -> list[RestaurantWeeklyHour]:
        await self._require_restaurant(organization_id, restaurant_id)

        validated_rows: list[RestaurantWeeklyHour] = []
        for day_item in days:
            dow = int(day_item["day_of_week"])
            if not 0 <= dow <= 6:
                raise ValidationDomainError(f"Invalid day_of_week '{dow}'; must be 0..6.")
            is_closed = bool(day_item.get("is_closed", False))
            raw_intervals = day_item.get("intervals", [])
            if is_closed:
                if raw_intervals:
                    raise ValidationDomainError("Closed day cannot specify opening intervals.")
                validated_rows.append(
                    RestaurantWeeklyHour(
                        organization_id=organization_id,
                        restaurant_id=restaurant_id,
                        day_of_week=dow,
                        is_closed=True,
                    )
                )
            else:
                intervals = [
                    OpeningInterval(
                        opens_at=_parse_time(iv["opens_at"]),
                        closes_at=_parse_time(iv["closes_at"]),
                        closes_next_day=bool(iv.get("closes_next_day", False)),
                    )
                    for iv in raw_intervals
                ]
                for iv in validate_daily_intervals(intervals):
                    validated_rows.append(
                        RestaurantWeeklyHour(
                            organization_id=organization_id,
                            restaurant_id=restaurant_id,
                            day_of_week=dow,
                            opens_at=iv.opens_at,
                            closes_at=iv.closes_at,
                            closes_next_day=iv.closes_next_day,
                            is_closed=False,
                        )
                    )

        await self.session.execute(
            delete(RestaurantWeeklyHour).where(
                RestaurantWeeklyHour.organization_id == organization_id,
                RestaurantWeeklyHour.restaurant_id == restaurant_id,
            )
        )
        for row in validated_rows:
            self.session.add(row)

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.schedule.updated",
            resource_type="restaurant_schedule",
            resource_id=restaurant_id,
            payload={"restaurant_id": str(restaurant_id), "rows": len(validated_rows)},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return validated_rows

    async def list_schedule_exceptions(
        self, organization_id: UUID, restaurant_id: UUID
    ) -> list[RestaurantScheduleException]:
        await self._require_restaurant(organization_id, restaurant_id)
        res = await self.session.execute(
            select(RestaurantScheduleException)
            .where(
                RestaurantScheduleException.organization_id == organization_id,
                RestaurantScheduleException.restaurant_id == restaurant_id,
            )
            .order_by(RestaurantScheduleException.exception_date)
        )
        return list(res.scalars().all())

    async def upsert_schedule_exception(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        exception_date: date,
        exception_type: str,
        reason: str | None = None,
        intervals: Sequence[dict[str, Any]] = (),
        correlation_id: str | None = None,
    ) -> RestaurantScheduleException:
        await self._require_restaurant(organization_id, restaurant_id)
        parsed_intervals = tuple(
            OpeningInterval(
                opens_at=_parse_time(iv["opens_at"]),
                closes_at=_parse_time(iv["closes_at"]),
                closes_next_day=bool(iv.get("closes_next_day", False)),
            )
            for iv in intervals
        )
        entry = ScheduleExceptionEntry(
            exception_date=exception_date,
            exception_type=ExceptionType(exception_type),
            reason=reason,
            intervals=parsed_intervals,
        )

        res = await self.session.execute(
            select(RestaurantScheduleException).where(
                RestaurantScheduleException.organization_id == organization_id,
                RestaurantScheduleException.restaurant_id == restaurant_id,
                RestaurantScheduleException.exception_date == exception_date,
            )
        )
        record = res.scalar_one_or_none()
        serialized_intervals = [
            {
                "opens_at": iv.opens_at.strftime("%H:%M:%S"),
                "closes_at": iv.closes_at.strftime("%H:%M:%S"),
                "closes_next_day": iv.closes_next_day,
            }
            for iv in entry.intervals
        ]
        if record is None:
            record = RestaurantScheduleException(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                exception_date=entry.exception_date,
                exception_type=entry.exception_type.value,
                reason=entry.reason,
                intervals_payload=serialized_intervals,
            )
            self.session.add(record)
        else:
            record.exception_type = entry.exception_type.value
            record.reason = entry.reason
            record.intervals_payload = serialized_intervals

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.schedule.exception.created",
            resource_type="restaurant_schedule_exception",
            resource_id=restaurant_id,
            payload={
                "restaurant_id": str(restaurant_id),
                "exception_date": exception_date.isoformat(),
                "exception_type": entry.exception_type.value,
            },
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return record

    async def delete_schedule_exception(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        exception_id: UUID,
    ) -> None:
        res = await self.session.execute(
            select(RestaurantScheduleException).where(
                RestaurantScheduleException.organization_id == organization_id,
                RestaurantScheduleException.restaurant_id == restaurant_id,
                RestaurantScheduleException.id == exception_id,
            )
        )
        record = res.scalar_one_or_none()
        if record is None:
            raise EntityNotFoundError(f"Schedule exception '{exception_id}' not found.")
        await self.session.delete(record)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Service Modes & Operational Settings
    # ------------------------------------------------------------------
    async def get_service_modes(
        self, organization_id: UUID, restaurant_id: UUID
    ) -> list[RestaurantServiceConfiguration]:
        await self._require_restaurant(organization_id, restaurant_id)
        res = await self.session.execute(
            select(RestaurantServiceConfiguration).where(
                RestaurantServiceConfiguration.organization_id == organization_id,
                RestaurantServiceConfiguration.restaurant_id == restaurant_id,
            )
        )
        return list(res.scalars().all())

    async def update_service_modes(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        modes: Sequence[dict[str, Any]],
        correlation_id: str | None = None,
    ) -> list[RestaurantServiceConfiguration]:
        await self._require_restaurant(organization_id, restaurant_id)
        existing_res = await self.session.execute(
            select(RestaurantServiceConfiguration).where(
                RestaurantServiceConfiguration.organization_id == organization_id,
                RestaurantServiceConfiguration.restaurant_id == restaurant_id,
            )
        )
        existing_map = {row.service_type: row for row in existing_res.scalars().all()}

        updated: list[RestaurantServiceConfiguration] = []
        for item in modes:
            cfg = ServiceModeConfig(
                service_type=ServiceType(item["service_type"]),
                enabled=bool(item["enabled"]),
                requires_customer_address=bool(item.get("requires_customer_address", False)),
                accepts_scheduled_orders=bool(item.get("accepts_scheduled_orders", False)),
                minimum_notice_minutes=int(item.get("minimum_notice_minutes", 0)),
            )
            payload = {
                "requires_customer_address": cfg.requires_customer_address,
                "accepts_scheduled_orders": cfg.accepts_scheduled_orders,
                "minimum_notice_minutes": cfg.minimum_notice_minutes,
            }
            row = existing_map.get(cfg.service_type.value)
            if row is None:
                row = RestaurantServiceConfiguration(
                    organization_id=organization_id,
                    restaurant_id=restaurant_id,
                    service_type=cfg.service_type.value,
                    enabled=cfg.enabled,
                    configuration=payload,
                )
                self.session.add(row)
            else:
                row.enabled = cfg.enabled
                row.configuration = payload
            updated.append(row)

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.service_configuration.updated",
            resource_type="restaurant_service_configuration",
            resource_id=restaurant_id,
            payload={"restaurant_id": str(restaurant_id), "count": len(updated)},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return updated

    async def get_operational_settings(
        self, organization_id: UUID, restaurant_id: UUID
    ) -> RestaurantOperationalSetting:
        await self._require_restaurant(organization_id, restaurant_id)
        res = await self.session.execute(
            select(RestaurantOperationalSetting).where(
                RestaurantOperationalSetting.organization_id == organization_id,
                RestaurantOperationalSetting.restaurant_id == restaurant_id,
            )
        )
        ops = res.scalar_one_or_none()
        if ops is None:
            ops = RestaurantOperationalSetting(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
            )
            self.session.add(ops)
            await self.session.flush()
        return ops

    async def update_operational_settings(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        actor_user_id: UUID,
        preparation_buffer_minutes: int,
        minimum_notice_minutes: int,
        maximum_advance_days: int,
        max_concurrent_orders: int | None = None,
        auto_accept_orders: bool = False,
        holiday_behavior: str = "follow_exceptions",
        correlation_id: str | None = None,
    ) -> RestaurantOperationalSetting:
        validated = OperationalSettings(
            preparation_buffer_minutes=preparation_buffer_minutes,
            minimum_notice_minutes=minimum_notice_minutes,
            maximum_advance_days=maximum_advance_days,
            max_concurrent_orders=max_concurrent_orders,
            auto_accept_orders=auto_accept_orders,
            holiday_behavior=holiday_behavior,
        )
        ops = await self.get_operational_settings(organization_id, restaurant_id)
        ops.preparation_buffer_minutes = validated.preparation_buffer_minutes
        ops.minimum_notice_minutes = validated.minimum_notice_minutes
        ops.maximum_advance_days = validated.maximum_advance_days
        ops.max_concurrent_orders = validated.max_concurrent_orders
        ops.auto_accept_orders = validated.auto_accept_orders
        ops.holiday_behavior = validated.holiday_behavior
        ops.revision += 1

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="restaurant.operations.updated",
            resource_type="restaurant_operational_settings",
            resource_id=restaurant_id,
            payload={"restaurant_id": str(restaurant_id), "revision": ops.revision},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return ops

    # ------------------------------------------------------------------
    # Branch Overrides & Effective Resolution
    # ------------------------------------------------------------------
    async def get_branch_configuration_record(
        self, organization_id: UUID, restaurant_id: UUID, branch_id: UUID
    ) -> BranchConfiguration:
        await self._require_branch(organization_id, restaurant_id, branch_id)
        res = await self.session.execute(
            select(BranchConfiguration).where(
                BranchConfiguration.organization_id == organization_id,
                BranchConfiguration.branch_id == branch_id,
            )
        )
        cfg = res.scalar_one_or_none()
        if cfg is None:
            cfg = BranchConfiguration(
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                branch_id=branch_id,
            )
            self.session.add(cfg)
            await self.session.flush()
        return cfg

    async def update_branch_configuration(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        branch_id: UUID,
        actor_user_id: UUID,
        display_name_override: str | None = None,
        public_phone_override: str | None = None,
        schedule_override_enabled: bool | None = None,
        service_override_enabled: bool | None = None,
        settings: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> BranchConfiguration:
        cfg = await self.get_branch_configuration_record(organization_id, restaurant_id, branch_id)
        if display_name_override is not None:
            cfg.display_name_override = display_name_override
        if public_phone_override is not None:
            cfg.public_phone_override = public_phone_override
        if schedule_override_enabled is not None:
            cfg.schedule_override_enabled = schedule_override_enabled
        if service_override_enabled is not None:
            cfg.service_override_enabled = service_override_enabled
        if settings is not None:
            cfg.settings = dict(settings)
        cfg.revision += 1

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="branch.configuration.updated",
            resource_type="branch_configuration",
            resource_id=branch_id,
            payload={"branch_id": str(branch_id), "revision": cfg.revision},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return cfg

    async def update_branch_service_modes(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        branch_id: UUID,
        actor_user_id: UUID,
        modes: Sequence[dict[str, Any]],
        correlation_id: str | None = None,
    ) -> list[BranchServiceConfiguration]:
        cfg = await self.get_branch_configuration_record(organization_id, restaurant_id, branch_id)
        cfg.service_override_enabled = True
        cfg.revision += 1

        existing_res = await self.session.execute(
            select(BranchServiceConfiguration).where(
                BranchServiceConfiguration.organization_id == organization_id,
                BranchServiceConfiguration.branch_id == branch_id,
            )
        )
        existing_map = {row.service_type: row for row in existing_res.scalars().all()}

        updated: list[BranchServiceConfiguration] = []
        for item in modes:
            svc_cfg = ServiceModeConfig(
                service_type=ServiceType(item["service_type"]),
                enabled=bool(item["enabled"]),
                requires_customer_address=bool(item.get("requires_customer_address", False)),
                accepts_scheduled_orders=bool(item.get("accepts_scheduled_orders", False)),
                minimum_notice_minutes=int(item.get("minimum_notice_minutes", 0)),
            )
            row = existing_map.get(svc_cfg.service_type.value)
            payload = {
                "requires_customer_address": svc_cfg.requires_customer_address,
                "accepts_scheduled_orders": svc_cfg.accepts_scheduled_orders,
                "minimum_notice_minutes": svc_cfg.minimum_notice_minutes,
            }
            if row is None:
                row = BranchServiceConfiguration(
                    organization_id=organization_id,
                    restaurant_id=restaurant_id,
                    branch_id=branch_id,
                    service_type=svc_cfg.service_type.value,
                    enabled=svc_cfg.enabled,
                    configuration=payload,
                )
                self.session.add(row)
            else:
                row.enabled = svc_cfg.enabled
                row.configuration = payload
            updated.append(row)

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="branch.configuration.updated",
            resource_type="branch_service_configuration",
            resource_id=branch_id,
            payload={"branch_id": str(branch_id), "services_updated": len(updated)},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return updated

    async def replace_branch_weekly_hours(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        branch_id: UUID,
        actor_user_id: UUID,
        days: Sequence[dict[str, Any]],
        correlation_id: str | None = None,
    ) -> list[BranchWeeklyHour]:
        cfg = await self.get_branch_configuration_record(organization_id, restaurant_id, branch_id)
        cfg.schedule_override_enabled = True
        cfg.revision += 1

        validated_rows: list[BranchWeeklyHour] = []
        for day_item in days:
            dow = int(day_item["day_of_week"])
            if not 0 <= dow <= 6:
                raise ValidationDomainError(f"Invalid day_of_week '{dow}'; must be 0..6.")
            is_closed = bool(day_item.get("is_closed", False))
            raw_intervals = day_item.get("intervals", [])
            if is_closed:
                validated_rows.append(
                    BranchWeeklyHour(
                        organization_id=organization_id,
                        restaurant_id=restaurant_id,
                        branch_id=branch_id,
                        day_of_week=dow,
                        is_closed=True,
                    )
                )
            else:
                intervals = [
                    OpeningInterval(
                        opens_at=_parse_time(iv["opens_at"]),
                        closes_at=_parse_time(iv["closes_at"]),
                        closes_next_day=bool(iv.get("closes_next_day", False)),
                    )
                    for iv in raw_intervals
                ]
                for iv in validate_daily_intervals(intervals):
                    validated_rows.append(
                        BranchWeeklyHour(
                            organization_id=organization_id,
                            restaurant_id=restaurant_id,
                            branch_id=branch_id,
                            day_of_week=dow,
                            opens_at=iv.opens_at,
                            closes_at=iv.closes_at,
                            closes_next_day=iv.closes_next_day,
                            is_closed=False,
                        )
                    )

        await self.session.execute(
            delete(BranchWeeklyHour).where(
                BranchWeeklyHour.organization_id == organization_id,
                BranchWeeklyHour.branch_id == branch_id,
            )
        )
        for row in validated_rows:
            self.session.add(row)

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="branch.configuration.updated",
            resource_type="branch_weekly_hours",
            resource_id=branch_id,
            payload={"branch_id": str(branch_id), "rows": len(validated_rows)},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return validated_rows

    async def reset_branch_configuration(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        branch_id: UUID,
        actor_user_id: UUID,
        reset_schedule: bool = True,
        reset_services: bool = True,
        correlation_id: str | None = None,
    ) -> BranchConfiguration:
        cfg = await self.get_branch_configuration_record(organization_id, restaurant_id, branch_id)
        if reset_schedule:
            cfg.schedule_override_enabled = False
            await self.session.execute(
                delete(BranchWeeklyHour).where(
                    BranchWeeklyHour.organization_id == organization_id,
                    BranchWeeklyHour.branch_id == branch_id,
                )
            )
        if reset_services:
            cfg.service_override_enabled = False
            await self.session.execute(
                delete(BranchServiceConfiguration).where(
                    BranchServiceConfiguration.organization_id == organization_id,
                    BranchServiceConfiguration.branch_id == branch_id,
                )
            )
        cfg.display_name_override = None
        cfg.public_phone_override = None
        cfg.revision += 1

        await self._record_event_and_audit(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            event_type="branch.configuration.updated",
            resource_type="branch_configuration_reset",
            resource_id=branch_id,
            payload={"branch_id": str(branch_id), "reset": True},
            correlation_id=correlation_id,
        )
        await self.session.flush()
        return cfg

    async def resolve_effective_configuration(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        branch_id: UUID | None = None,
    ) -> EffectiveRestaurantConfiguration:
        org, rest = await self._require_restaurant(organization_id, restaurant_id)
        profile = await self.get_profile(organization_id, restaurant_id)
        branding_row = await self.get_branding(organization_id, restaurant_id)
        ops_row = await self.get_operational_settings(organization_id, restaurant_id)
        svc_rows = await self.get_service_modes(organization_id, restaurant_id)
        hour_rows = await self.get_weekly_hours(organization_id, restaurant_id)
        exc_rows = await self.list_schedule_exceptions(organization_id, restaurant_id)

        branding_entity = RestaurantBrandingEntity(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            logo_asset_id=branding_row.logo_asset_id,
            alternate_logo_asset_id=branding_row.alternate_logo_asset_id,
            cover_asset_id=branding_row.cover_asset_id,
            favicon_asset_id=branding_row.favicon_asset_id,
            primary_color=(
                HexColor(branding_row.primary_color) if branding_row.primary_color else None
            ),
            secondary_color=(
                HexColor(branding_row.secondary_color) if branding_row.secondary_color else None
            ),
            accent_color=(
                HexColor(branding_row.accent_color) if branding_row.accent_color else None
            ),
            background_color=(
                HexColor(branding_row.background_color) if branding_row.background_color else None
            ),
            text_color=HexColor(branding_row.text_color) if branding_row.text_color else None,
            font_family=branding_row.font_family,
            border_radius=branding_row.border_radius,
            theme_preset=branding_row.theme_preset,
            theme_settings=dict(branding_row.theme_settings or {}),
        )

        rest_services = {
            row.service_type: ServiceModeConfig(
                service_type=ServiceType(row.service_type),
                enabled=row.enabled,
                requires_customer_address=bool(
                    (row.configuration or {}).get("requires_customer_address", False)
                ),
                accepts_scheduled_orders=bool(
                    (row.configuration or {}).get("accepts_scheduled_orders", False)
                ),
                minimum_notice_minutes=int(
                    (row.configuration or {}).get("minimum_notice_minutes", 0)
                ),
            )
            for row in svc_rows
        }

        rest_hours: dict[int, list[OpeningInterval]] = {}
        for row in hour_rows:
            if not row.is_closed and row.opens_at and row.closes_at:
                rest_hours.setdefault(row.day_of_week, []).append(
                    OpeningInterval(
                        opens_at=row.opens_at,
                        closes_at=row.closes_at,
                        closes_next_day=row.closes_next_day,
                    )
                )
        rest_hours_tuple = {k: tuple(v) for k, v in rest_hours.items()}

        exceptions_tuple = tuple(
            ScheduleExceptionEntry(
                exception_date=row.exception_date,
                exception_type=ExceptionType(row.exception_type),
                reason=row.reason,
                intervals=tuple(
                    OpeningInterval(
                        opens_at=_parse_time(iv["opens_at"]),
                        closes_at=_parse_time(iv["closes_at"]),
                        closes_next_day=bool(iv.get("closes_next_day", False)),
                    )
                    for iv in (row.intervals_payload or [])
                ),
            )
            for row in exc_rows
        )

        ops_vo = OperationalSettings(
            preparation_buffer_minutes=ops_row.preparation_buffer_minutes,
            minimum_notice_minutes=ops_row.minimum_notice_minutes,
            maximum_advance_days=ops_row.maximum_advance_days,
            max_concurrent_orders=ops_row.max_concurrent_orders,
            auto_accept_orders=ops_row.auto_accept_orders,
            holiday_behavior=ops_row.holiday_behavior,
        )

        branch_tz: str | None = None
        branch_phone: str | None = None
        branch_entity: BranchConfigurationEntity | None = None

        if branch_id is not None:
            branch = await self._require_branch(organization_id, restaurant_id, branch_id)
            branch_tz = branch.timezone
            branch_phone = branch.phone
            b_cfg_res = await self.session.execute(
                select(BranchConfiguration).where(
                    BranchConfiguration.organization_id == organization_id,
                    BranchConfiguration.branch_id == branch_id,
                )
            )
            b_cfg = b_cfg_res.scalar_one_or_none()
            if b_cfg is not None:
                b_svc_res = await self.session.execute(
                    select(BranchServiceConfiguration).where(
                        BranchServiceConfiguration.organization_id == organization_id,
                        BranchServiceConfiguration.branch_id == branch_id,
                    )
                )
                b_services = {
                    row.service_type: ServiceModeConfig(
                        service_type=ServiceType(row.service_type),
                        enabled=row.enabled,
                        requires_customer_address=bool(
                            (row.configuration or {}).get("requires_customer_address", False)
                        ),
                        accepts_scheduled_orders=bool(
                            (row.configuration or {}).get("accepts_scheduled_orders", False)
                        ),
                        minimum_notice_minutes=int(
                            (row.configuration or {}).get("minimum_notice_minutes", 0)
                        ),
                    )
                    for row in b_svc_res.scalars().all()
                }
                b_hr_res = await self.session.execute(
                    select(BranchWeeklyHour).where(
                        BranchWeeklyHour.organization_id == organization_id,
                        BranchWeeklyHour.branch_id == branch_id,
                    )
                )
                b_hours: dict[int, list[OpeningInterval]] = {}
                for row in b_hr_res.scalars().all():
                    if not row.is_closed and row.opens_at and row.closes_at:
                        b_hours.setdefault(row.day_of_week, []).append(
                            OpeningInterval(
                                opens_at=row.opens_at,
                                closes_at=row.closes_at,
                                closes_next_day=row.closes_next_day,
                            )
                        )
                branch_entity = BranchConfigurationEntity(
                    organization_id=organization_id,
                    restaurant_id=restaurant_id,
                    branch_id=branch_id,
                    display_name_override=b_cfg.display_name_override,
                    public_phone_override=b_cfg.public_phone_override,
                    schedule_override_enabled=b_cfg.schedule_override_enabled,
                    service_override_enabled=b_cfg.service_override_enabled,
                    service_overrides=b_services,
                    weekly_hours_override={k: tuple(v) for k, v in b_hours.items()},
                )

        return build_effective_configuration(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            restaurant_name=profile.public_name or rest.name,
            restaurant_timezone=rest.timezone,
            organization_currency=org.currency_code,
            restaurant_phone=profile.public_phone or rest.phone,
            restaurant_services=rest_services,
            restaurant_weekly_hours=rest_hours_tuple,
            restaurant_exceptions=exceptions_tuple,
            branding=branding_entity,
            restaurant_operational_settings=ops_vo,
            branch_id=branch_id,
            branch_timezone=branch_tz,
            branch_phone=branch_phone,
            branch_config=branch_entity,
            revision=profile.version,
        )

    async def evaluate_open_now(
        self,
        *,
        organization_id: UUID,
        restaurant_id: UUID,
        branch_id: UUID | None = None,
        now_utc: datetime | None = None,
    ) -> OpenStatusResult:
        effective = await self.resolve_effective_configuration(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            branch_id=branch_id,
        )
        return evaluate_open_status(
            now_utc=now_utc or datetime.now(UTC),
            timezone_name=effective.timezone,
            weekly_hours=effective.weekly_hours,
            exceptions=effective.schedule_exceptions,
        )
