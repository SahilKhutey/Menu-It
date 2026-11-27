"""Contact value objects for email addresses (FCD-06 §7.4)."""

import re
from dataclasses import dataclass

from menu_it.domain.base.errors import ValidationDomainError

_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@dataclass(frozen=True, slots=True)
class EmailAddress:
    """Canonical email address value object."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValidationDomainError("Email address must be a string.")
        normalized = self.value.strip().casefold()
        if not normalized:
            raise ValidationDomainError("Email address cannot be empty.")
        if len(normalized) > 320:
            raise ValidationDomainError("Email address is too long (max 320 characters).")
        if not _EMAIL_REGEX.fullmatch(normalized):
            raise ValidationDomainError("Invalid email address format.")
        object.__setattr__(self, "value", normalized)
