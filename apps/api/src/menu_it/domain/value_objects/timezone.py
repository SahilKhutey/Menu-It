"""Time zone value object validating standard IANA identifiers (FCD-06 §9.3)."""

from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from menu_it.domain.base.errors import ValidationDomainError


@dataclass(frozen=True, slots=True)
class TimeZone:
    """Canonical IANA time zone identifier value object (e.g. 'Asia/Kolkata', 'UTC')."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationDomainError("Time zone name must be a non-empty string.")
        normalized = self.name.strip()
        try:
            ZoneInfo(normalized)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValidationDomainError(
                f"Unknown or invalid IANA time zone identifier: '{normalized}'."
            ) from exc
        object.__setattr__(self, "name", normalized)
