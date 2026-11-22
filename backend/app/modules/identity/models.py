import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import GUID, Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_platform_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)

    memberships: Mapped[list["RestaurantMember"]] = relationship(
        "RestaurantMember", back_populates="user", cascade="all, delete-orphan", lazy="raise"
    )


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)

    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant", back_populates="organization", cascade="all, delete-orphan", lazy="raise"
    )


class Restaurant(Base, TimestampMixin):
    __tablename__ = "restaurants"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="restaurants", lazy="raise"
    )
    members: Mapped[list["RestaurantMember"]] = relationship(
        "RestaurantMember", back_populates="restaurant", cascade="all, delete-orphan", lazy="raise"
    )
    menus: Mapped[list[Any]] = relationship(
        "Menu", back_populates="restaurant", cascade="all, delete-orphan", lazy="raise"
    )


class RestaurantMember(Base, TimestampMixin):
    __tablename__ = "restaurant_members"
    __table_args__ = (UniqueConstraint("restaurant_id", "user_id", name="uq_restaurant_user"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(40), default="menu_editor", nullable=False)
    # Roles: 'owner', 'manager', 'menu_editor', 'viewer'

    user: Mapped["User"] = relationship("User", back_populates="memberships", lazy="raise")
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant", back_populates="members", lazy="raise"
    )
