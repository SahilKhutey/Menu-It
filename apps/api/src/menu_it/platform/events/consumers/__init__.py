"""Event consumers package initialization (FCD-10 WP-08)."""

from menu_it.platform.events.consumers.handlers import (
    handle_file_uploaded,
    handle_notification_requested,
    handle_user_registered,
)

__all__ = [
    "handle_file_uploaded",
    "handle_notification_requested",
    "handle_user_registered",
]
