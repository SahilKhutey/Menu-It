"""Core domain value objects (FCD-06 §7)."""

from menu_it.domain.value_objects.address import Address
from menu_it.domain.value_objects.contact import EmailAddress
from menu_it.domain.value_objects.currency import SUPPORTED_CURRENCIES, Currency
from menu_it.domain.value_objects.money import Money
from menu_it.domain.value_objects.operating_hours import (
    DailyOperatingHours,
    Weekday,
    WeeklyOperatingSchedule,
)
from menu_it.domain.value_objects.percentage import Percentage, TaxRate
from menu_it.domain.value_objects.phone_number import PhoneNumber
from menu_it.domain.value_objects.slug import Slug
from menu_it.domain.value_objects.time_range import TimeRange
from menu_it.domain.value_objects.timezone import TimeZone

__all__ = [
    "SUPPORTED_CURRENCIES",
    "Address",
    "Currency",
    "DailyOperatingHours",
    "EmailAddress",
    "Money",
    "Percentage",
    "PhoneNumber",
    "Slug",
    "TaxRate",
    "TimeRange",
    "TimeZone",
    "Weekday",
    "WeeklyOperatingSchedule",
]
