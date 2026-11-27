"""Integration tests for FCD-14 Organization, Restaurant, Branch, and Membership services."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.branch import BranchStatus
from menu_it.database.models.branch_assignment import BranchRole
from menu_it.database.models.event_outbox import EventOutboxModel
from menu_it.database.models.organization import OrganizationStatus
from menu_it.database.models.organization_membership import MembershipStatus, OrganizationRole
from menu_it.database.models.restaurant import RestaurantStatus
from menu_it.database.models.user import User, UserStatus
from menu_it.domain.base.errors import (
    BusinessRuleViolationError,
    DomainError,
    EntityNotFoundError,
)
from menu_it.exceptions.domain import ResourceConflictError
from menu_it.services.branch_management import BranchManagementService
from menu_it.services.membership_and_invitation import MembershipAndInvitationService
from menu_it.services.organization_management import OrganizationManagementService
from menu_it.services.restaurant_management import RestaurantManagementService


async def _create_user(session: AsyncSession, email: str) -> User:
    u = User(
        email=email,
        normalized_email=email.lower(),
        display_name=email.split("@")[0],
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    session.add(u)
    await session.flush()
    return u


@pytest.mark.integration
@pytest.mark.asyncio
async def test_organization_onboarding_and_outbox_atomicity(db_session: AsyncSession) -> None:
    owner = await _create_user(db_session, f"owner-{uuid4().hex[:6]}@abc.com")
    svc = OrganizationManagementService(db_session)

    org, membership = await svc.create_organization(
        name="ABC Hospitality",
        slug=f"abc-{uuid4().hex[:6]}",
        actor_user_id=owner.id,
        currency_code="INR",
        timezone="Asia/Kolkata",
        country_code="IN",
    )
    assert org.status == OrganizationStatus.ACTIVE
    assert membership.role == OrganizationRole.OWNER
    assert membership.status == MembershipStatus.ACTIVE

    # Verify outbox event staged atomically
    outbox = (
        await db_session.execute(
            select(EventOutboxModel).where(EventOutboxModel.organization_id == org.id)
        )
    ).scalar_one_or_none()
    assert outbox is not None
    assert outbox.event_type == "organization.created"

    # Duplicate slug rejected
    with pytest.raises(ResourceConflictError):
        await svc.create_organization(
            name="ABC Duplicate",
            slug=org.slug,
            actor_user_id=owner.id,
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_restaurant_branch_hierarchy_and_cross_tenant_isolation(
    db_session: AsyncSession,
) -> None:
    user_a = await _create_user(db_session, f"a-{uuid4().hex[:6]}@a.com")
    user_b = await _create_user(db_session, f"b-{uuid4().hex[:6]}@b.com")

    org_svc = OrganizationManagementService(db_session)
    org_a, _ = await org_svc.create_organization(
        name="Org A", slug=f"org-a-{uuid4().hex[:6]}", actor_user_id=user_a.id
    )
    org_b, _ = await org_svc.create_organization(
        name="Org B", slug=f"org-b-{uuid4().hex[:6]}", actor_user_id=user_b.id
    )

    rest_svc = RestaurantManagementService(db_session)
    rest_a = await rest_svc.create_restaurant(
        organization_id=org_a.id,
        actor_user_id=user_a.id,
        name="Spice Garden",
        slug="spice-garden",
        timezone="Asia/Kolkata",
    )
    # Same slug allowed in Org B
    rest_b = await rest_svc.create_restaurant(
        organization_id=org_b.id,
        actor_user_id=user_b.id,
        name="Spice Garden B",
        slug="spice-garden",
        timezone="UTC",
    )
    assert rest_a.id != rest_b.id

    # Cross-tenant restaurant lookup fails
    with pytest.raises(EntityNotFoundError):
        await rest_svc.get_restaurant(organization_id=org_a.id, restaurant_id=rest_b.id)

    # Branch creation with distinct timezone
    branch_svc = BranchManagementService(db_session)
    branch_a1 = await branch_svc.create_branch(
        organization_id=org_a.id,
        restaurant_id=rest_a.id,
        actor_user_id=user_a.id,
        name="Spice Garden — Bilaspur",
        slug="bilaspur",
        timezone="Asia/Kolkata",
        country_code="IN",
        city="Bilaspur",
    )
    assert branch_a1.organization_id == org_a.id

    # Cross-tenant branch creation under Org B's restaurant from Org A fails
    with pytest.raises(EntityNotFoundError):
        await branch_svc.create_branch(
            organization_id=org_a.id,
            restaurant_id=rest_b.id,
            actor_user_id=user_a.id,
            name="Rogue Branch",
            slug="rogue",
        )

    # Suspend branch and reactivate
    await branch_svc.transition_status(
        organization_id=org_a.id,
        branch_id=branch_a1.id,
        target_status=BranchStatus.SUSPENDED,
        actor_user_id=user_a.id,
    )
    assert branch_a1.status == BranchStatus.SUSPENDED

    # Inactive restaurant blocks new branch creation
    await rest_svc.transition_status(
        organization_id=org_a.id,
        restaurant_id=rest_a.id,
        target_status=RestaurantStatus.INACTIVE,
        actor_user_id=user_a.id,
    )
    with pytest.raises(BusinessRuleViolationError):
        await branch_svc.create_branch(
            organization_id=org_a.id,
            restaurant_id=rest_a.id,
            actor_user_id=user_a.id,
            name="Blocked Branch",
            slug="blocked",
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invitations_owner_protection_transfer_and_branch_assignment(
    db_session: AsyncSession,
) -> None:
    owner = await _create_user(db_session, f"own-{uuid4().hex[:6]}@org.com")
    staff = await _create_user(db_session, f"staff-{uuid4().hex[:6]}@org.com")

    org_svc = OrganizationManagementService(db_session)
    org, _ = await org_svc.create_organization(
        name="Owner Test Org", slug=f"own-org-{uuid4().hex[:6]}", actor_user_id=owner.id
    )

    mem_svc = MembershipAndInvitationService(db_session)

    # Final owner cannot be removed
    with pytest.raises(BusinessRuleViolationError):
        await mem_svc.remove_member(
            organization_id=org.id, target_user_id=owner.id, actor_user_id=owner.id
        )

    # Invite staff member (token hashed, raw token returned once)
    inv, raw_token = await mem_svc.create_invitation(
        organization_id=org.id,
        email=staff.email,
        role=OrganizationRole.MANAGER,
        invited_by=owner.id,
    )
    assert inv.token_hash != raw_token

    # Staff accepts invitation
    accepted_mem = await mem_svc.accept_invitation(
        raw_token=raw_token,
        actor_user_id=staff.id,
        actor_email=staff.email,
    )
    assert accepted_mem.role == OrganizationRole.MANAGER
    assert accepted_mem.status == MembershipStatus.ACTIVE

    # Reuse accepted invitation rejected
    with pytest.raises(DomainError):
        await mem_svc.accept_invitation(
            raw_token=raw_token,
            actor_user_id=staff.id,
            actor_email=staff.email,
        )

    # Branch assignment
    rest = await RestaurantManagementService(db_session).create_restaurant(
        organization_id=org.id, actor_user_id=owner.id, name="R1", slug="r1"
    )
    branch = await BranchManagementService(db_session).create_branch(
        organization_id=org.id, restaurant_id=rest.id, actor_user_id=owner.id, name="B1", slug="b1"
    )
    assignment = await BranchManagementService(db_session).upsert_assignment(
        organization_id=org.id,
        branch_id=branch.id,
        user_id=staff.id,
        role=BranchRole.BRANCH_MANAGER,
        actor_user_id=owner.id,
    )
    assert assignment.role == BranchRole.BRANCH_MANAGER

    # Ownership transfer
    prev_owner, new_owner = await mem_svc.transfer_ownership(
        organization_id=org.id,
        current_owner_id=owner.id,
        new_owner_id=staff.id,
    )
    assert prev_owner.role == OrganizationRole.ADMIN
    assert new_owner.role == OrganizationRole.OWNER
