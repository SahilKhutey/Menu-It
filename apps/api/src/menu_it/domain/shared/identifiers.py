"""Strongly typed domain entity identifiers (FCD-06 §6.5)."""

from typing import NewType
from uuid import UUID

OrganizationId = NewType("OrganizationId", UUID)
RestaurantId = NewType("RestaurantId", UUID)
UserId = NewType("UserId", UUID)
DomainEventId = NewType("DomainEventId", UUID)

__all__ = [
    "DomainEventId",
    "OrganizationId",
    "RestaurantId",
    "UserId",
]
