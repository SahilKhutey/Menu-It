"""Tenant database model (FCD-03 §9.2)."""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from menu_it.database.models.restaurant import Restaurant


class TenantStatus(enum.StrEnum):
    """Lifecycle status of a tenant account."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class Tenant(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Foundational organization/account tenant record."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus, name="tenant_status", native_enum=False),
        default=TenantStatus.ACTIVE,
        nullable=False,
    )

    # Relationship to owned restaurants; foreign key ondelete=RESTRICT enforces retention
    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant",
        back_populates="tenant",
        passive_deletes="all",
    )
