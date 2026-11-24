"""Organization domain references and identity contracts (FCD-06 §8.1)."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrganizationReference:
    """Lightweight domain reference to a tenant organization."""

    organization_id: UUID
    display_name: str | None = None
