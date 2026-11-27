"""FCD-15 Restaurant configuration, branding, schedule, service, and publication ORM models."""

import uuid
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RestaurantBranding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Visual identity, asset references, and validated theme settings."""

    __tablename__ = "restaurant_branding"
    __table_args__ = (
        UniqueConstraint("organization_id", "restaurant_id", name="uq_restaurant_branding"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_branding_restaurant",
            ondelete="CASCADE",
        ),
        Index("ix_restaurant_branding_org_id", "organization_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    logo_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    alternate_logo_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    cover_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    favicon_asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    secondary_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    accent_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    background_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    text_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    font_family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    border_radius: Mapped[str | None] = mapped_column(String(20), nullable=True)
    theme_preset: Mapped[str | None] = mapped_column(String(60), nullable=True)
    theme_settings: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class RestaurantWeeklyHour(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Normalized weekly operating schedule shift for a restaurant."""

    __tablename__ = "restaurant_weekly_hours"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_restaurant_weekly_weekday"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_weekly_hours_restaurant",
            ondelete="CASCADE",
        ),
        Index("ix_restaurant_weekly_hours_rest_day", "restaurant_id", "day_of_week"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    opens_at: Mapped[time | None] = mapped_column(Time, nullable=True)
    closes_at: Mapped[time | None] = mapped_column(Time, nullable=True)
    closes_next_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class RestaurantScheduleException(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Date-specific holiday closure or special hours for a restaurant."""

    __tablename__ = "restaurant_schedule_exceptions"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "exception_date",
            name="uq_restaurant_schedule_exception_date",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_schedule_exception_restaurant",
            ondelete="CASCADE",
        ),
        Index("ix_restaurant_schedule_exc_rest_date", "restaurant_id", "exception_date"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    exception_date: Mapped[date] = mapped_column(Date, nullable=False)
    exception_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(250), nullable=True)
    intervals_payload: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
    )


class RestaurantServiceConfiguration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Fulfillment service mode configuration at restaurant level."""

    __tablename__ = "restaurant_service_configurations"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "service_type",
            name="uq_restaurant_service",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_service_restaurant",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_type: Mapped[str] = mapped_column(String(40), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )


class RestaurantOperationalSetting(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Operational preferences (prep buffer, advance window, capacity)."""

    __tablename__ = "restaurant_operational_settings"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            name="uq_restaurant_operational_settings",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_operational_restaurant",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    preparation_buffer_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    minimum_notice_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    maximum_advance_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    max_concurrent_orders: Mapped[int | None] = mapped_column(Integer, nullable=True)
    auto_accept_orders: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    holiday_behavior: Mapped[str] = mapped_column(
        String(40), nullable=False, default="follow_exceptions"
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class BranchConfiguration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Explicit branch-level configuration overrides."""

    __tablename__ = "branch_configurations"
    __table_args__ = (
        UniqueConstraint("organization_id", "branch_id", name="uq_branch_configuration"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_configuration_parent",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    display_name_override: Mapped[str | None] = mapped_column(String(200), nullable=True)
    public_phone_override: Mapped[str | None] = mapped_column(String(30), nullable=True)
    schedule_override_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    service_override_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class BranchWeeklyHour(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Branch-specific weekly operating schedule shift."""

    __tablename__ = "branch_weekly_hours"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_branch_weekly_weekday"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_weekly_hours_branch",
            ondelete="CASCADE",
        ),
        Index("ix_branch_weekly_hours_branch_day", "branch_id", "day_of_week"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    opens_at: Mapped[time | None] = mapped_column(Time, nullable=True)
    closes_at: Mapped[time | None] = mapped_column(Time, nullable=True)
    closes_next_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class BranchServiceConfiguration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Explicit branch-level service mode override."""

    __tablename__ = "branch_service_configurations"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "branch_id",
            "service_type",
            name="uq_branch_service",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_service_branch",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_type: Mapped[str] = mapped_column(String(40), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )


class RestaurantPublication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Current public profile publication state and pointer."""

    __tablename__ = "restaurant_publications"
    __table_args__ = (
        UniqueConstraint("organization_id", "restaurant_id", name="uq_restaurant_publication"),
        UniqueConstraint("public_slug", name="uq_restaurant_publication_slug"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_publication_restaurant",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    public_slug: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    published_revision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class RestaurantConfigurationRevision(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Immutable revision snapshot history for restaurant configuration & publication."""

    __tablename__ = "restaurant_configuration_revisions"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "revision_number",
            name="uq_restaurant_config_revision",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_config_revision_restaurant",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(String(250), nullable=True)
