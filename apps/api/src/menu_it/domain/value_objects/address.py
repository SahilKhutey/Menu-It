"""Physical address value object (FCD-06 §7.7)."""

from dataclasses import dataclass

from menu_it.domain.base.errors import ValidationDomainError


@dataclass(frozen=True, slots=True)
class Address:
    """International postal address value object."""

    line_1: str
    locality: str
    country_code: str
    line_2: str | None = None
    administrative_area: str | None = None
    postal_code: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.line_1, str) or not self.line_1.strip():
            raise ValidationDomainError("Address line 1 is required.")
        if not isinstance(self.locality, str) or not self.locality.strip():
            raise ValidationDomainError("Locality (city/town) is required.")
        if not isinstance(self.country_code, str):
            raise ValidationDomainError("Country code must be a string.")

        normalized_country = self.country_code.strip().upper()
        if len(normalized_country) != 2 or not normalized_country.isalpha():
            raise ValidationDomainError(
                "Country code must be an ISO 3166-1 alpha-2 code (2 letters)."
            )

        object.__setattr__(self, "line_1", self.line_1.strip())
        object.__setattr__(self, "locality", self.locality.strip())
        object.__setattr__(self, "country_code", normalized_country)

        if self.line_2 is not None:
            clean_l2 = self.line_2.strip() or None
            object.__setattr__(self, "line_2", clean_l2)

        if self.administrative_area is not None:
            clean_area = self.administrative_area.strip() or None
            object.__setattr__(self, "administrative_area", clean_area)

        if self.postal_code is not None:
            clean_pc = self.postal_code.strip() or None
            object.__setattr__(self, "postal_code", clean_pc)
