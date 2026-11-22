"""
ModularMenu — Database Declarative Base & Model Mixins (ARC-06 §4.1, §4.2, §8.2).
Provides canonical primary keys, UTC timestamping, and tenant/restaurant scoping mixins.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.database import GUID

# Standardized constraint naming conventions (ARC-06 §4.1)
POSTGRES_NAMING_CONVENTIONS = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTIONS)


class Base(DeclarativeBase):
    """ARC-06 Data Architecture Declarative Base."""

    metadata = metadata


class UUIDPrimaryKey:
    """UUID Primary key mixin using platform-independent GUID."""

    id: Mapped[UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid4,
    )


class Timestamped:
    """UTC-aware timestamping mixin (created_at and updated_at)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class ImmutableTimestamped:
    """UTC-aware creation timestamp for immutable entities (snapshots, audit logs)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class TenantScoped:
    """Primary tenant boundary scoping mixin (organization_id)."""

    organization_id: Mapped[UUID] = mapped_column(
        GUID(),
        nullable=False,
        index=True,
    )


class RestaurantScoped(TenantScoped):
    """Subordinate restaurant branch scoping mixin (organization_id + restaurant_id)."""

    restaurant_id: Mapped[UUID] = mapped_column(
        GUID(),
        nullable=False,
        index=True,
    )
