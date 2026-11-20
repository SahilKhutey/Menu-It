"""
ModularMenu — Presentation & Design Configuration Models (ARC-06 §3.2, §5.3).
Platform theme presets, tenant custom themes, versioned design configurations, and component schemas.
"""
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID, PortableJSON
from app.shared.infrastructure.database.base import Base, Timestamped, UUIDPrimaryKey


class ThemeModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "themes"

    owner_organization_id: Mapped[Optional[UUID]] = mapped_column(GUID(), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    theme_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    tokens: Mapped[Dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    is_system_preset: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RestaurantDesignConfigModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "restaurant_design_configs"
    __table_args__ = (
        UniqueConstraint("organization_id", "restaurant_id", name="uq_design_config_restaurant"),
        ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_design_config_restaurant",
            ondelete="CASCADE",
        ),
        CheckConstraint("schema_version > 0", name="ck_design_config_schema_version"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    restaurant_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    theme_key: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[Dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)


class LayoutPresetModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "layout_presets"

    owner_organization_id: Mapped[Optional[UUID]] = mapped_column(GUID(), nullable=True, index=True)
    layout_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    config: Mapped[Dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)


class ComponentDefinitionModel(Base, UUIDPrimaryKey, Timestamped):
    __tablename__ = "component_definitions"

    component_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    definition: Mapped[Dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
