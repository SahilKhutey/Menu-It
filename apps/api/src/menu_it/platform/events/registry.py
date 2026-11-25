"""Event consumer registry and dispatcher (FCD-10 WP-05)."""

import logging
from typing import Any, Callable

logger = logging.getLogger("menu_it.platform.events.registry")

EVENT_CONSUMER_REGISTRY: dict[str, list[Callable[..., Any]]] = {}


def register_consumer(event_type: str, handler: Callable[..., Any]) -> None:
    """Register an event handler function for an event type."""
    if event_type not in EVENT_CONSUMER_REGISTRY:
        EVENT_CONSUMER_REGISTRY[event_type] = []
    EVENT_CONSUMER_REGISTRY[event_type].append(handler)


def get_consumers(event_type: str) -> list[Callable[..., Any]]:
    """Retrieve all registered consumer handlers for an event type."""
    return EVENT_CONSUMER_REGISTRY.get(event_type, [])
