"""
ModularMenu — Publication & Versioning Persistence Models (ARC-06 §3.2, §6.2, ARC-10 §8).
Immutable menu snapshots with SHA-256 verification and active publication pointers.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID, PortableJSON
from app.shared.infrastructure.database.base import Base, UUIDPrimaryKey
from app.shared.infrastructure.database.immutability import register_immutability_guard


class MenuVersionModel(Base, UUIDPrimaryKey):
    __tablename__ = "menu_versions"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "menu_id",
            "version_number",
            name="uq_menu_versions_number",
        ),
        UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "menu_id",
            "id",
            name="uq_menu_versions_org_restaurant_menu_id",
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "menu_id"],
            ["menus.organization_id", "menus.restaurant_id", "menus.id"],
            name="fk_menu_versions_menu",
            ondelete="CASCADE",
        ),
        CheckConstraint("version_number > 0", name="ck_menu_versions_positive"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    snapshot_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    content_schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    design_schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


# Enforce database and ORM immutability (ARC-06 §6.4, ARC-10 §8.5)
register_immutability_guard(MenuVersionModel)


class PublicationModel(Base, UUIDPrimaryKey):
    __tablename__ = "publications"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "restaurant_id", "menu_id", name="uq_publications_active_menu"
        ),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "menu_id", "menu_version_id"],
            [
                "menu_versions.organization_id",
                "menu_versions.restaurant_id",
                "menu_versions.menu_id",
                "menu_versions.id",
            ],
            name="fk_publications_menu_version",
            ondelete="CASCADE",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_version_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


# ARC-10 Extended Persistence Models (§8)


class DraftRevisionModel(Base, UUIDPrimaryKey):
    __tablename__ = "menu_draft_revisions"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "menu_id", "revision_number", name="uq_draft_revision_number"
        ),
        CheckConstraint("revision_number > 0", name="ck_draft_revision_positive"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    revision_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    parent_revision_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


register_immutability_guard(DraftRevisionModel)


class PublicationSnapshotModel(Base, UUIDPrimaryKey):
    __tablename__ = "menu_publication_snapshots"
    __table_args__ = (
        UniqueConstraint("organization_id", "menu_id", "id", name="uq_snapshot_scope"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    schema_version: Mapped[str] = mapped_column(String(32), default="1.0", nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


register_immutability_guard(PublicationSnapshotModel)


class PublicationActivationModel(Base, UUIDPrimaryKey):
    __tablename__ = "publication_activations"

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    publication_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    previous_publication_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    operation_id: Mapped[UUID] = mapped_column(GUID(), nullable=False)
    activation_reason: Mapped[str] = mapped_column(String(32), default="publish", nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )


register_immutability_guard(PublicationActivationModel)


class ScheduledPublicationModel(Base, UUIDPrimaryKey):
    __tablename__ = "scheduled_publications"

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    menu_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    draft_revision: Mapped[int] = mapped_column(BigInteger, nullable=False)
    expected_active_publication_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timezone_name: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="SCHEDULED", nullable=False)
    created_by: Mapped[UUID] = mapped_column(GUID(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
