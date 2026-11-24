"""Unit tests for TimeZone value object (FCD-06 §9.3)."""

import pytest

from menu_it.domain.base.errors import ValidationDomainError
from menu_it.domain.value_objects.timezone import TimeZone


def test_timezone_valid_iana() -> None:
    tz1 = TimeZone("Asia/Kolkata")
    assert tz1.name == "Asia/Kolkata"

    tz2 = TimeZone("UTC")
    assert tz2.name == "UTC"

    tz3 = TimeZone("America/New_York")
    assert tz3.name == "America/New_York"


def test_timezone_invalid_iana_rejected() -> None:
    with pytest.raises(ValidationDomainError):
        TimeZone("Invalid/Timezone")

    with pytest.raises(ValidationDomainError):
        TimeZone("UTC+05:30")  # Fixed offset is not an IANA identifier

    with pytest.raises(ValidationDomainError):
        TimeZone("")

    with pytest.raises(ValidationDomainError):
        TimeZone(None)  # type: ignore[arg-type]
