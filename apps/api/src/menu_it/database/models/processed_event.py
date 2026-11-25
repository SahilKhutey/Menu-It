"""SQLAlchemy model for consumer inbox event deduplication (FCD-10 WP-05)."""

from datetime import datetime
import uuid

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from menu_it.database.base import Base


class ProcessedEventModel(Base):
    """Consumer inbox tracking processed events to ensure at-most-once execution."""

    __tablename__ = "processed_events"

    consumer_name: Mapped[str] = mapped_column(
        String(150),
        primary_key=True,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
