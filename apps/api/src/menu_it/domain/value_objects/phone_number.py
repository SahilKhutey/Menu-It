"""International phone number value object in canonical E.164 format (FCD-06 §7.5)."""

from dataclasses import dataclass

import phonenumbers
from phonenumbers import NumberParseException

from menu_it.domain.base.errors import ValidationDomainError


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """Canonical E.164 international telephone number value object."""

    e164: str

    def __post_init__(self) -> None:
        if not isinstance(self.e164, str):
            raise ValidationDomainError("Phone number must be a string.")
        if not self.e164.startswith("+"):
            raise ValidationDomainError("Canonical E.164 phone number must start with '+'.")

    @classmethod
    def parse(cls, raw: str, region: str | None = None) -> "PhoneNumber":
        """Parse, validate, and format raw input telephone number to canonical E.164."""
        if not raw or not isinstance(raw, str):
            raise ValidationDomainError("Raw phone number string is required.")
        try:
            parsed = phonenumbers.parse(raw.strip(), region)
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationDomainError(
                    f"Phone number '{raw}' is not a valid telephone number."
                )
            formatted = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164,
            )
            return cls(e164=formatted)
        except NumberParseException as exc:
            raise ValidationDomainError(f"Unable to parse phone number '{raw}': {exc}") from exc
