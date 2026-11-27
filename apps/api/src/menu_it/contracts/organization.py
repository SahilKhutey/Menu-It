"""Organization API response contracts (FCD-06 §12.4)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationReferenceResponse(BaseModel):
    """Organization reference payload for API responses."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    name: str
    slug: str
