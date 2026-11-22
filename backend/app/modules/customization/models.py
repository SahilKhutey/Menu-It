"""
ModularMenu — Customization Persistence Models (ARC-08 §14, ARC-06 §3.2).
Provides relational tenancy ownership, optimistic revision tracking, and immutable revision history.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import GUID, Base, PortableJSON, TimestampMixin


class MenuCustomization(Base, TimestampMixin):
    __tablename__ = "menu_customizations"
    __table_args__ = (
        UniqueConstraint("organization_id", "menu_id", name="uq_customization_org_menu"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    revision: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)

    revisions: Mapped[list["CustomizationRevision"]] = relationship(
        "CustomizationRevision",
        back_populates="customization",
        cascade="all, delete-orphan",
        lazy="raise",
    )


class CustomizationRevision(Base):
    __tablename__ = "customization_revisions"
    __table_args__ = (
        UniqueConstraint("customization_id", "revision", name="uq_customization_revision_num"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    customization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("menu_customizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    customization: Mapped["MenuCustomization"] = relationship(
        "MenuCustomization", back_populates="revisions", lazy="raise"
    )
