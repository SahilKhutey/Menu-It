"""
ModularMenu — Organization & Tenancy Models (ARC-06 §3.2, §4.3).
Primary tenant boundary entities, memberships, and pending invitations.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID
from app.shared.infrastructure.database.base import Base, Timestamped, UUIDPrimaryKey


class OrganizationModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "organizations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'suspended', 'deletion_pending', 'deleted')",
            name="ck_organizations_status",
        ),
    )

    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)


class OrganizationMemberModel(Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'admin', 'org_admin', 'manager', 'restaurant_manager', 'editor', 'menu_editor', 'viewer', 'member')",
            name="ck_org_members_role",
        ),
        CheckConstraint(
            "status IN ('invited', 'active', 'suspended')",
            name="ck_org_members_status",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(40), default="member", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class OrganizationInvitationModel(Base, UUIDPrimaryKey):
    __tablename__ = "organization_invitations"
    __table_args__ = (
        UniqueConstraint("organization_id", "email", name="uq_org_invitation_email"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), default="editor", nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
