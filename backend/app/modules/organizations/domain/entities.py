"""
Organization Domain Entities (ARC-04 §6.2, MOD-02).
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


@dataclass
class Organization:
    id: UUID
    name: str
    owner_id: UUID
    is_active: bool = True
    member_ids: set[UUID] = field(default_factory=set)

    def __post_init__(self) -> None:
        normalized = self.name.strip()
        if not normalized:
            raise ValueError("Organization name cannot be empty")
        self.name = normalized
        # Owner is inherently an active member
        self.member_ids.add(self.owner_id)

    def add_member(self, user_id: UUID) -> None:
        if not self.is_active:
            raise ValueError("Organization is inactive")
        self.member_ids.add(user_id)

    def remove_member(self, user_id: UUID) -> None:
        if user_id == self.owner_id:
            raise ValueError("Cannot remove the organization owner")
        self.member_ids.discard(user_id)

    def transfer_ownership(self, new_owner_id: UUID) -> None:
        if new_owner_id not in self.member_ids:
            raise ValueError("New owner must be an existing organization member")
        self.owner_id = new_owner_id


@dataclass
class Invitation:
    id: UUID
    organization_id: UUID
    email: str
    role: str = "member"
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_accepted: bool = False

    def assert_can_accept(self) -> None:
        if self.is_accepted:
            raise ValueError("Invitation is already accepted")
        if datetime.now(timezone.utc) > self.expires_at:
            raise ValueError("Invitation has expired")
