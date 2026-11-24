"""Canonical organization database model (FCD-04 §6.2)."""

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
    from menu_it.database.models.organization_membership import OrganizationMembership
    from menu_it.database.models.restaurant import Restaurant


class OrganizationStatus(enum.StrEnum):
    """Lifecycle status of an organization account."""

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    OFFBOARDING = "offboarding"
    DEACTIVATED = "deactivated"


class Organization(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Canonical primary tenant organization record."""

    __tablename__ = "organizations"

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
    status: Mapped[OrganizationStatus] = mapped_column(
        Enum(OrganizationStatus, name="organization_status", native_enum=False),
        default=OrganizationStatus.PROVISIONING,
        nullable=False,
    )

    # Relationships
    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant",
        back_populates="organization",
        passive_deletes="all",
    )
    memberships: Mapped[list["OrganizationMembership"]] = relationship(
        "OrganizationMembership",
        back_populates="organization",
        passive_deletes="all",
    )


# Backward-compatibility aliases for FCD-03 references
Tenant = Organization
TenantStatus = OrganizationStatus
