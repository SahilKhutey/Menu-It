import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID, Base, PortableJSON, TimestampMixin


class Theme(Base, TimestampMixin):
    __tablename__ = "themes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    theme_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    tokens: Mapped[dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    is_system_preset: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RestaurantDesignConfig(Base, TimestampMixin):
    __tablename__ = "restaurant_design_configs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("restaurants.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    theme_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("themes.id"), nullable=False)
    layout_config: Mapped[dict[str, Any]] = mapped_column(
        PortableJSON(),
        default=lambda: {"type": "category_first", "card_style": "compact"},
        nullable=False,
    )
    component_config: Mapped[dict[str, Any]] = mapped_column(
        PortableJSON(), default=dict, nullable=False
    )
    custom_tokens: Mapped[dict[str, Any]] = mapped_column(
        PortableJSON(), default=dict, nullable=False
    )
    config_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
