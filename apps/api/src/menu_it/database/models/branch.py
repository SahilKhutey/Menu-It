"""Branch database model representing physical restaurant locations (FCD-14 §5.4)."""

import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from menu_it.database.models.branch_assignment import BranchAssignment
    from menu_it.database.models.restaurant import Restaurant


class BranchStatus(enum.StrEnum):
    """Lifecycle status of a physical restaurant branch."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class Branch(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Physical or operational location belonging to a restaurant within an organization."""

    __tablename__ = "branches"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_branch_restaurant_tenant",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "id",
            name="uq_branch_org_restaurant_id",
        ),
        UniqueConstraint(
            "restaurant_id",
            "slug",
            name="uq_branches_restaurant_slug",
        ),
        Index("ix_branches_org_id", "organization_id"),
        Index("ix_branches_restaurant_id", "restaurant_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address_line_1: Mapped[str | None] = mapped_column(String(250), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(250), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state_region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    country_code: Mapped[str] = mapped_column(
        String(2), nullable=False, default="IN", server_default="IN"
    )
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(100), nullable=False, default="UTC", server_default="UTC"
    )
    status: Mapped[BranchStatus] = mapped_column(
        Enum(BranchStatus, name="branch_status", native_enum=False),
        default=BranchStatus.ACTIVE,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
        back_populates="branches",
    )
    assignments: Mapped[list["BranchAssignment"]] = relationship(
        "BranchAssignment",
        back_populates="branch",
        passive_deletes="all",
    )
