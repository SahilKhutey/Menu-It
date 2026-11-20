"""
ModularMenu — Commercial & Licensing Persistence Models (ARC-06 §3.2).
Platform subscription plans, organization subscriptions, and appliance license entitlements.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID
from app.shared.infrastructure.database.base import Base, Timestamped, UUIDPrimaryKey


class SubscriptionPlanModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "subscription_plans"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    max_branches: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    custom_themes_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    price_minor: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)


class SubscriptionModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_subscriptions_org"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("subscription_plans.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LicenseModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "licenses"

    organization_id: Mapped[UUID] = mapped_column(
        GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    license_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    edition: Mapped[str] = mapped_column(String(50), default="saas", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
