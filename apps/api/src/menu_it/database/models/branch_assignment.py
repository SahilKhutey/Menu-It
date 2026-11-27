"""Branch assignment database model (FCD-14 §5.6)."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from menu_it.database.models.organization_membership import MembershipStatus

if TYPE_CHECKING:
    from menu_it.database.models.branch import Branch


class BranchRole(enum.StrEnum):
    """Role within a specific physical branch."""

    BRANCH_MANAGER = "branch_manager"
    BRANCH_STAFF = "branch_staff"


class BranchAssignment(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Assignment linking a user to a specific branch within a restaurant and organization."""

    __tablename__ = "branch_assignments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_assignment_tenant_branch",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "branch_id",
            "user_id",
            name="uq_branch_assignment_branch_user",
        ),
        Index("ix_branch_assignments_org_id", "organization_id"),
        Index("ix_branch_assignments_branch_id", "branch_id"),
        Index("ix_branch_assignments_user_id", "user_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[BranchRole] = mapped_column(
        Enum(BranchRole, name="branch_role", native_enum=False),
        nullable=False,
        default=BranchRole.BRANCH_STAFF,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="branch_assignment_status", native_enum=False),
        nullable=False,
        default=MembershipStatus.ACTIVE,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    branch: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="assignments",
    )
