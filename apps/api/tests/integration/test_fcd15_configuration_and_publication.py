"""Integration tests for FCD-15 configuration, resolver, overrides, and publication."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.event_outbox import EventOutboxModel
from menu_it.database.models.user import User, UserStatus
from menu_it.domain.base.errors import (
    ConcurrencyConflictError,
    EntityNotFoundError,
    ValidationDomainError,
)
from menu_it.services.branch_management import BranchManagementService
from menu_it.services.organization_management import OrganizationManagementService
from menu_it.services.restaurant_configuration import RestaurantConfigurationService
from menu_it.services.restaurant_management import RestaurantManagementService
from menu_it.services.restaurant_publication import RestaurantPublicationService


async def _seed_user(session: AsyncSession) -> User:
    u = User(
        email=f"owner-{uuid4().hex[:6]}@menu-it.com",
        normalized_email=f"owner-{uuid4().hex[:6]}@menu-it.com",
        display_name="Owner",
        status=UserStatus.ACTIVE,
        email_verified=True,
    )
    session.add(u)
    await session.flush()
    return u


@pytest.mark.asyncio
async def test_fcd15_configuration_resolution_and_concurrency(db_session: AsyncSession) -> None:
    owner = await _seed_user(db_session)
    org, _ = await OrganizationManagementService(db_session).create_organization(
        actor_user_id=owner.id,
        name="Hospitality Group",
        slug=f"hosp-{uuid4().hex[:6]}",
        currency_code="INR",
        timezone="Asia/Kolkata",
    )
    rest = await RestaurantManagementService(db_session).create_restaurant(
        organization_id=org.id,
        actor_user_id=owner.id,
        name="Bistro One",
        slug=f"bistro-{uuid4().hex[:6]}",
        timezone="Asia/Kolkata",
    )
    branch = await BranchManagementService(db_session).create_branch(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        name="Bistro West",
        slug="west",
        timezone="Europe/London",
    )

    cfg_svc = RestaurantConfigurationService(db_session)
    profile = await cfg_svc.update_profile(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        display_name="Bistro One Kitchen",
        cuisine_type="Modern Indian",
        expected_version=1,
    )
    assert profile.version == 2

    # Optimistic concurrency mismatch rejected
    with pytest.raises(ConcurrencyConflictError):
        await cfg_svc.update_profile(
            organization_id=org.id,
            restaurant_id=rest.id,
            actor_user_id=owner.id,
            display_name="Stale Update",
            expected_version=1,
        )

    # Invalid hex color rejected
    with pytest.raises(ValidationDomainError):
        await cfg_svc.update_branding(
            organization_id=org.id,
            restaurant_id=rest.id,
            actor_user_id=owner.id,
            primary_color="not-a-hex",
        )

    branding = await cfg_svc.update_branding(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        primary_color="#112233",
        font_family="Inter",
    )
    assert branding.primary_color == "#112233"

    await cfg_svc.update_service_modes(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        modes=[
            {"service_type": "DINE_IN", "enabled": True},
            {"service_type": "DELIVERY", "enabled": True},
        ],
    )

    # Branch explicitly disables DELIVERY
    await cfg_svc.update_branch_service_modes(
        organization_id=org.id,
        restaurant_id=rest.id,
        branch_id=branch.id,
        actor_user_id=owner.id,
        modes=[{"service_type": "DELIVERY", "enabled": False}],
    )

    effective = await cfg_svc.resolve_effective_configuration(
        organization_id=org.id,
        restaurant_id=rest.id,
        branch_id=branch.id,
    )
    assert effective.timezone == "Europe/London"
    assert effective.enabled_services == ("DINE_IN",)

    # Reset branch overrides -> inherits DELIVERY again
    await cfg_svc.reset_branch_configuration(
        organization_id=org.id,
        restaurant_id=rest.id,
        branch_id=branch.id,
        actor_user_id=owner.id,
    )
    effective_after_reset = await cfg_svc.resolve_effective_configuration(
        organization_id=org.id,
        restaurant_id=rest.id,
        branch_id=branch.id,
    )
    assert effective_after_reset.enabled_services == ("DELIVERY", "DINE_IN")


@pytest.mark.asyncio
async def test_fcd15_publication_privacy_and_revision_restore(db_session: AsyncSession) -> None:
    owner = await _seed_user(db_session)
    org, _ = await OrganizationManagementService(db_session).create_organization(
        actor_user_id=owner.id,
        name="Pub Group",
        slug=f"pub-{uuid4().hex[:6]}",
    )
    rest = await RestaurantManagementService(db_session).create_restaurant(
        organization_id=org.id,
        actor_user_id=owner.id,
        name="Cafe Alpha",
        slug=f"alpha-{uuid4().hex[:6]}",
    )

    cfg_svc = RestaurantConfigurationService(db_session)
    await cfg_svc.update_service_modes(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        modes=[{"service_type": "DINE_IN", "enabled": True}],
    )
    await cfg_svc.upsert_schedule_exception(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        exception_date=date(2026, 12, 25),
        exception_type="CLOSED",
        reason="Christmas",
    )

    pub_svc = RestaurantPublicationService(db_session)
    slug = f"cafe-alpha-{uuid4().hex[:6]}"
    pub1 = await pub_svc.publish(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        public_slug=slug,
    )
    assert pub1.published_revision == 1

    public_view = await pub_svc.get_public_profile_by_slug(slug)
    assert public_view["display_name"] == "Cafe Alpha"
    assert "organization_id" not in public_view
    assert "restaurant_id" not in public_view

    # Update profile and publish revision 2
    await cfg_svc.update_profile(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        display_name="Cafe Alpha v2",
    )
    pub2 = await pub_svc.publish(
        organization_id=org.id,
        restaurant_id=rest.id,
        actor_user_id=owner.id,
        public_slug=slug,
    )
    assert pub2.published_revision == 2

    # Unpublish revokes public access
    await pub_svc.unpublish(organization_id=org.id, restaurant_id=rest.id, actor_user_id=owner.id)
    with pytest.raises(EntityNotFoundError):
        await pub_svc.get_public_profile_by_slug(slug)

    # Restore revision 1
    restored = await pub_svc.restore_revision(
        organization_id=org.id,
        restaurant_id=rest.id,
        revision_number=1,
        actor_user_id=owner.id,
    )
    assert restored.published_revision == 1
    restored_public = await pub_svc.get_public_profile_by_slug(slug)
    assert restored_public["display_name"] == "Cafe Alpha"

    outbox_res = await db_session.execute(
        select(EventOutboxModel).where(EventOutboxModel.organization_id == org.id)
    )
    event_types = {ev.event_type for ev in outbox_res.scalars().all()}
    assert "restaurant.profile.published" in event_types
    assert "restaurant.profile.unpublished" in event_types
