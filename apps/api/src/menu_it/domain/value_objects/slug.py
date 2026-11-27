"""Slug value object for URL-safe identifiers (FCD-06 §7.6)."""

import re
from dataclasses import dataclass

from menu_it.domain.base.errors import ValidationDomainError

_SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class Slug:
    """URL-safe kebab-case slug value object."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValidationDomainError("Slug must be a string.")
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValidationDomainError("Slug cannot be empty.")
        if len(normalized) > 100:
            raise ValidationDomainError("Slug cannot exceed 100 characters.")
        if not _SLUG_REGEX.fullmatch(normalized):
            raise ValidationDomainError(
                f"Invalid slug format '{normalized}'. "
                "Slugs must contain lowercase alphanumeric characters and single hyphens."
            )
        object.__setattr__(self, "value", normalized)
