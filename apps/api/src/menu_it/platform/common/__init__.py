"""Common platform utilities package."""

from menu_it.platform.common.clock import Clock, FrozenClock, SystemClock
from menu_it.platform.common.identifiers import new_uuid, parse_uuid
from menu_it.platform.common.localization import DEFAULT_LOCALE, SUPPORTED_LOCALES, resolve_locale
from menu_it.platform.common.pagination import PageRequest
from menu_it.platform.common.serialization import serialize_value
from menu_it.platform.common.timezone import get_timezone, now_in_timezone, to_local_time

__all__ = [
    "Clock",
    "DEFAULT_LOCALE",
    "FrozenClock",
    "PageRequest",
    "SUPPORTED_LOCALES",
    "SystemClock",
    "get_timezone",
    "new_uuid",
    "now_in_timezone",
    "parse_uuid",
    "resolve_locale",
    "serialize_value",
    "to_local_time",
]
