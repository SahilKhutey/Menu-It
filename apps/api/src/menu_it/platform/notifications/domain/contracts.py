"""Notification domain contracts and value objects (FCD-09 WP-03)."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable
from uuid import UUID


class NotificationChannel(StrEnum):
    """Supported notification delivery channels."""

    EMAIL = "email"
    IN_APP = "in_app"


class NotificationStatus(StrEnum):
    """Lifecycle and delivery states of a notification."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class NotificationMessage:
    """Message payload for dispatching a notification across channels."""

    notification_id: UUID
    recipient: str
    template_id: str
    locale: str = "en"
    variables: dict[str, str] = field(default_factory=dict)
    idempotency_key: str = ""
    organization_id: UUID | None = None
    channel: NotificationChannel = NotificationChannel.EMAIL


@dataclass(frozen=True)
class NotificationResult:
    """Outcome of attempting to send a notification."""

    provider_reference: str | None
    accepted: bool
    status: NotificationStatus = NotificationStatus.ACCEPTED
    error: str | None = None


@runtime_checkable
class NotificationChannelAdapter(Protocol):
    """Protocol for a delivery channel adapter (Email, In-App, etc.)."""

    async def send(self, message: NotificationMessage) -> NotificationResult:
        """Deliver the notification message through this channel."""
        ...
