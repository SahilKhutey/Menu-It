"""Organization invitation database model (FCD-14 §5.1, §8.2)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base
from menu_it.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from menu_it.database.models.organization_membership import OrganizationRole
from menu_it.domain.invitation.entities import InvitationStatus


class OrganizationInvitation(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    """Pending or historical invitation to join an organization."""

    __tablename__ = "organization_invitations"
    __table_args__ = (
        Index("ix_org_invitations_org_id", "organization_id"),
        Index("ix_org_invitations_email", "email"),
        Index("ix_org_invitations_token_hash", "token_hash", unique=True),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    role: Mapped[OrganizationRole] = mapped_column(
        Enum(OrganizationRole, name="invitation_role", native_enum=False),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus, name="invitation_status", native_enum=False),
        nullable=False,
        default=InvitationStatus.PENDING,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invited_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    accepted_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
