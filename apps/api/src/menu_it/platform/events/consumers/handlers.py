"""Concrete event consumer handlers (FCD-10 WP-08)."""

import logging

from menu_it.platform.events.contracts import EventEnvelope

logger = logging.getLogger("menu_it.platform.events.consumers")


async def handle_notification_requested(event: EventEnvelope, services: any) -> None:
    """Consume NotificationRequested events."""
    logger.info(f"Consuming NotificationRequested event: {event.event_id}")


async def handle_file_uploaded(event: EventEnvelope, services: any) -> None:
    """Consume FileUploaded events."""
    logger.info(f"Consuming FileUploaded event: {event.event_id}")


async def handle_user_registered(event: EventEnvelope, services: any) -> None:
    """Consume UserRegistered events."""
    logger.info(f"Consuming UserRegistered event: {event.event_id}")
