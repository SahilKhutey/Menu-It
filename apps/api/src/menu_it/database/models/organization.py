"""Canonical organization database model (FCD-04 §6.2, FCD-14 §5.2)."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
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

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    legal_name: Mapped[str | None] = mapped_column(String(250), nullable=True)
    organization_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="company", server_default="company"
    )
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    country_code: Mapped[str] = mapped_column(
        String(2), nullable=False, default="IN", server_default="IN"
    )
    currency_code: Mapped[str] = mapped_column(
        String(3), nullable=False, default="INR", server_default="INR"
    )
    timezone: Mapped[str] = mapped_column(
        String(100), nullable=False, default="UTC", server_default="UTC"
    )
    status: Mapped[OrganizationStatus] = mapped_column(
        Enum(OrganizationStatus, name="organization_status", native_enum=False),
        default=OrganizationStatus.PROVISIONING,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
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
