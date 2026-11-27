"""Organization membership, ownership transfer & invitation service (FCD-14 WP-06, WP-09)."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.audit import OrganizationAuditEvent
from menu_it.database.models.organization_invitation import OrganizationInvitation
from menu_it.database.models.organization_membership import (
    MembershipStatus,
    OrganizationMembership,
    OrganizationRole,
)
from menu_it.domain.base.errors import BusinessRuleViolationError, EntityNotFoundError
from menu_it.domain.invitation.entities import InvitationStatus, OrganizationInvitationEntity
from menu_it.domain.invitation.lifecycle import ensure_invitation_acceptable
from menu_it.domain.membership.policies import ensure_not_removing_final_owner
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.publisher import OutboxEventPublisher


def _hash_invitation_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class MembershipAndInvitationService:
    """Application service for organization memberships, owner protection, and invitations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.outbox = OutboxEventPublisher(session)

    async def list_members(self, organization_id: UUID) -> list[OrganizationMembership]:
        """List all memberships for an organization."""
        result = await self.session.execute(
            select(OrganizationMembership)
            .where(OrganizationMembership.organization_id == organization_id)
            .order_by(OrganizationMembership.created_at.asc())
        )
        return list(result.scalars().all())

    async def _count_active_owners(self, organization_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(OrganizationMembership)
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.role == OrganizationRole.OWNER,
                OrganizationMembership.status == MembershipStatus.ACTIVE,
            )
        )
        return int((await self.session.execute(stmt)).scalar_one())

    async def update_member(
        self,
        *,
        organization_id: UUID,
        target_user_id: UUID,
        actor_user_id: UUID,
        role: OrganizationRole | None = None,
        status: MembershipStatus | None = None,
        correlation_id: str | None = None,
    ) -> OrganizationMembership:
        """Update a member's role or status while enforcing final active owner protection."""
        membership = (
            await self.session.execute(
                select(OrganizationMembership).where(
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.user_id == target_user_id,
                )
            )
        ).scalar_one_or_none()
        if membership is None:
            raise EntityNotFoundError("Organization membership not found.")

        is_active_owner = (
            membership.role == OrganizationRole.OWNER
            and membership.status == MembershipStatus.ACTIVE
        )
        active_owners = await self._count_active_owners(organization_id)
        ensure_not_removing_final_owner(
            active_owner_count=active_owners,
            target_is_active_owner=is_active_owner,
            new_role=role.value if role else None,
            new_status=status.value if status else None,
        )

        if role is not None:
            membership.role = role
        if status is not None:
            membership.status = status
        membership.updated_by = actor_user_id

        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=actor_user_id,
                action="organization.member.updated",
                resource_type="organization_membership",
                resource_id=str(membership.id),
                correlation_id=correlation_id,
                metadata_={
                    "target_user_id": str(target_user_id),
                    "role": membership.role.value,
                    "status": membership.status.value,
                },
            )
        )
        await self.session.flush()
        return membership

    async def remove_member(
        self,
        *,
        organization_id: UUID,
        target_user_id: UUID,
        actor_user_id: UUID,
        correlation_id: str | None = None,
    ) -> OrganizationMembership:
        """Revoke an organization member while preventing removal of the final active owner."""
        membership = await self.update_member(
            organization_id=organization_id,
            target_user_id=target_user_id,
            actor_user_id=actor_user_id,
            status=MembershipStatus.REVOKED,
            correlation_id=correlation_id,
        )
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="organization.member.removed",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"target_user_id": str(target_user_id)},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return membership

    async def transfer_ownership(
        self,
        *,
        organization_id: UUID,
        current_owner_id: UUID,
        new_owner_id: UUID,
        correlation_id: str | None = None,
    ) -> tuple[OrganizationMembership, OrganizationMembership]:
        """Atomically transfer organization ownership to another active member."""
        if current_owner_id == new_owner_id:
            raise BusinessRuleViolationError("New owner must be a different user.")

        current_owner = (
            await self.session.execute(
                select(OrganizationMembership).where(
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.user_id == current_owner_id,
                    OrganizationMembership.status == MembershipStatus.ACTIVE,
                    OrganizationMembership.role == OrganizationRole.OWNER,
                )
            )
        ).scalar_one_or_none()
        if current_owner is None:
            raise BusinessRuleViolationError("Actor is not an active owner of this organization.")

        new_owner = (
            await self.session.execute(
                select(OrganizationMembership).where(
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.user_id == new_owner_id,
                    OrganizationMembership.status == MembershipStatus.ACTIVE,
                )
            )
        ).scalar_one_or_none()
        if new_owner is None:
            raise EntityNotFoundError("Target user does not hold an active membership.")

        new_owner.role = OrganizationRole.OWNER
        new_owner.updated_by = current_owner_id
        current_owner.role = OrganizationRole.ADMIN
        current_owner.updated_by = current_owner_id

        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=current_owner_id,
                action="organization.owner.transferred",
                resource_type="organization",
                resource_id=str(organization_id),
                correlation_id=correlation_id,
                metadata_={
                    "previous_owner_id": str(current_owner_id),
                    "new_owner_id": str(new_owner_id),
                },
            )
        )
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="organization.owner.transferred",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=current_owner_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"new_owner_id": str(new_owner_id)},
                occurred_at=datetime.now(UTC),
            )
        )
        await self.session.flush()
        return current_owner, new_owner

    async def create_invitation(
        self,
        *,
        organization_id: UUID,
        email: str,
        role: OrganizationRole,
        invited_by: UUID,
        ttl_hours: int = 168,
        correlation_id: str | None = None,
    ) -> tuple[OrganizationInvitation, str]:
        """Create a pending invitation with a hashed secure token and outbox event."""
        if role == OrganizationRole.OWNER:
            raise BusinessRuleViolationError("Cannot invite directly as organization owner.")

        clean_email = email.strip().lower()
        existing_pending = (
            await self.session.execute(
                select(OrganizationInvitation).where(
                    OrganizationInvitation.organization_id == organization_id,
                    OrganizationInvitation.email == clean_email,
                    OrganizationInvitation.status == InvitationStatus.PENDING,
                )
            )
        ).scalar_one_or_none()
        if existing_pending is not None:
            raise ResourceConflictError("A pending invitation already exists for this email.")

        raw_token = secrets.token_urlsafe(32)
        now = datetime.now(UTC)
        invitation = OrganizationInvitation(
            organization_id=organization_id,
            email=clean_email,
            role=role,
            token_hash=_hash_invitation_token(raw_token),
            status=InvitationStatus.PENDING,
            expires_at=now + timedelta(hours=ttl_hours),
            invited_by=invited_by,
        )
        self.session.add(invitation)
        await self.session.flush()

        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=invited_by,
                action="organization.member.invited",
                resource_type="organization_invitation",
                resource_id=str(invitation.id),
                correlation_id=correlation_id,
                metadata_={"role": role.value},
            )
        )
        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="organization.member.invited",
                schema_version=1,
                organization_id=organization_id,
                actor_user_id=invited_by,
                correlation_id=correlation_id or str(uuid4()),
                payload={"invitation_id": str(invitation.id), "role": role.value},
                occurred_at=now,
            )
        )
        await self.session.flush()
        return invitation, raw_token

    async def list_invitations(self, organization_id: UUID) -> list[OrganizationInvitation]:
        """List invitations for an organization."""
        result = await self.session.execute(
            select(OrganizationInvitation)
            .where(OrganizationInvitation.organization_id == organization_id)
            .order_by(OrganizationInvitation.created_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_invitation(
        self,
        *,
        organization_id: UUID,
        invitation_id: UUID,
        actor_user_id: UUID,
    ) -> OrganizationInvitation:
        """Revoke a pending invitation."""
        inv = (
            await self.session.execute(
                select(OrganizationInvitation).where(
                    OrganizationInvitation.id == invitation_id,
                    OrganizationInvitation.organization_id == organization_id,
                )
            )
        ).scalar_one_or_none()
        if inv is None:
            raise EntityNotFoundError("Invitation not found.")
        if inv.status != InvitationStatus.PENDING:
            raise BusinessRuleViolationError(
                f"Cannot revoke invitation in '{inv.status.value}' state."
            )
        inv.status = InvitationStatus.REVOKED
        self.session.add(
            OrganizationAuditEvent(
                organization_id=organization_id,
                actor_id=actor_user_id,
                action="organization.invitation.revoked",
                resource_type="organization_invitation",
                resource_id=str(inv.id),
                metadata_={},
            )
        )
        await self.session.flush()
        return inv

    async def accept_invitation(
        self,
        *,
        raw_token: str,
        actor_user_id: UUID,
        actor_email: str,
        correlation_id: str | None = None,
    ) -> OrganizationMembership:
        """Validate and accept an invitation token, creating or activating membership."""
        token_hash = _hash_invitation_token(raw_token)
        inv = (
            await self.session.execute(
                select(OrganizationInvitation).where(
                    OrganizationInvitation.token_hash == token_hash
                )
            )
        ).scalar_one_or_none()
        if inv is None:
            raise EntityNotFoundError("Invalid invitation token.")

        now = datetime.now(UTC)
        # Ensure timezone-aware comparison even if SQLite returned naive datetime
        expires_at = (
            inv.expires_at.replace(tzinfo=UTC) if inv.expires_at.tzinfo is None else inv.expires_at
        )
        created_at = (
            inv.created_at.replace(tzinfo=UTC) if inv.created_at.tzinfo is None else inv.created_at
        )
        domain_inv = OrganizationInvitationEntity(
            id=inv.id,
            organization_id=inv.organization_id,
            email=inv.email,
            role=inv.role.value,
            status=inv.status,
            expires_at=expires_at,
            created_at=created_at,
            invited_by=inv.invited_by,
        )
        ensure_invitation_acceptable(domain_inv, now=now, actor_email=actor_email)

        inv.status = InvitationStatus.ACCEPTED
        inv.accepted_by = actor_user_id
        inv.accepted_at = now

        existing_member = (
            await self.session.execute(
                select(OrganizationMembership).where(
                    OrganizationMembership.organization_id == inv.organization_id,
                    OrganizationMembership.user_id == actor_user_id,
                )
            )
        ).scalar_one_or_none()

        if existing_member is not None:
            existing_member.role = inv.role
            existing_member.status = MembershipStatus.ACTIVE
            existing_member.joined_at = now
            existing_member.updated_by = actor_user_id
            membership = existing_member
        else:
            membership = OrganizationMembership(
                organization_id=inv.organization_id,
                user_id=actor_user_id,
                role=inv.role,
                status=MembershipStatus.ACTIVE,
                joined_at=now,
                created_by=actor_user_id,
                updated_by=actor_user_id,
            )
            self.session.add(membership)

        await self.outbox.publish(
            EventEnvelope(
                event_id=uuid4(),
                event_type="organization.member.joined",
                schema_version=1,
                organization_id=inv.organization_id,
                actor_user_id=actor_user_id,
                correlation_id=correlation_id or str(uuid4()),
                payload={"membership_role": inv.role.value},
                occurred_at=now,
            )
        )
        await self.session.flush()
        return membership
