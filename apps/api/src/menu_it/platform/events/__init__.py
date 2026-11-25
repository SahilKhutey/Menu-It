"""Event platform package initialization (FCD-10 WP-05)."""

from menu_it.platform.events.consumers import (
    handle_file_uploaded,
    handle_notification_requested,
    handle_user_registered,
)
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.dispatcher import OutboxDispatcher
from menu_it.platform.events.inbox import EventInbox
from menu_it.platform.events.publisher import OutboxEventPublisher
from menu_it.platform.events.registry import (
    EVENT_CONSUMER_REGISTRY,
    get_consumers,
    register_consumer,
)

# Register default core consumers
register_consumer("NotificationRequested", handle_notification_requested)
register_consumer("FileUploaded", handle_file_uploaded)
register_consumer("UserRegistered", handle_user_registered)

__all__ = [
    "EVENT_CONSUMER_REGISTRY",
    "EventEnvelope",
    "EventInbox",
    "OutboxDispatcher",
    "OutboxEventPublisher",
    "get_consumers",
    "handle_file_uploaded",
    "handle_notification_requested",
    "handle_user_registered",
    "register_consumer",
]
