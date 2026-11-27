"""Unit tests for FCD-14 domain entities, invariants, and policies (WP-01, §13.1–13.4)."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from menu_it.domain.base.errors import (
    BusinessRuleViolationError,
    InvalidStateTransitionError,
    ValidationDomainError,
)
from menu_it.domain.branch import (
    BranchEntity,
    BranchLifecycleState,
    validate_branch_transition,
)
from menu_it.domain.invitation import (
    InvitationStatus,
    OrganizationInvitationEntity,
    ensure_invitation_acceptable,
)
from menu_it.domain.membership import (
    BranchAssignmentEntity,
    OrganizationMembershipEntity,
    ensure_not_removing_final_owner,
    ensure_same_organization_scope,
)
from menu_it.domain.organization.entities import OrganizationEntity


def test_organization_entity_validation() -> None:
    now = datetime.now(UTC)
    org = OrganizationEntity(
        id=uuid4(),
        name="ABC Hospitality",
        slug="abc-hospitality",
        status="active",
        country_code="IN",
        currency_code="INR",
        timezone="Asia/Kolkata",
        created_at=now,
        updated_at=now,
    )
    assert org.currency_code == "INR"

    with pytest.raises(ValidationDomainError):
        OrganizationEntity(
            id=uuid4(),
            name="A",
            slug="abc",
            status="active",
            country_code="IN",
            currency_code="INR",
            timezone="Asia/Kolkata",
            created_at=now,
            updated_at=now,
        )

    with pytest.raises(ValidationDomainError):
        OrganizationEntity(
            id=uuid4(),
            name="ABC Hospitality",
            slug="abc",
            status="active",
            country_code="IND",
            currency_code="INR",
            timezone="Asia/Kolkata",
            created_at=now,
            updated_at=now,
        )


def test_branch_entity_and_lifecycle() -> None:
    now = datetime.now(UTC)
    branch = BranchEntity(
        id=uuid4(),
        organization_id=uuid4(),
        restaurant_id=uuid4(),
        name="Spice Garden — Bilaspur",
        slug="bilaspur",
        timezone="Asia/Kolkata",
        country_code="IN",
        status="active",
        latitude=Decimal("22.0797"),
        longitude=Decimal("82.1409"),
        created_at=now,
        updated_at=now,
    )
    assert branch.name == "Spice Garden — Bilaspur"

    validate_branch_transition(BranchLifecycleState.ACTIVE, BranchLifecycleState.SUSPENDED)
    validate_branch_transition(BranchLifecycleState.SUSPENDED, BranchLifecycleState.ACTIVE)
    validate_branch_transition(BranchLifecycleState.ACTIVE, BranchLifecycleState.ARCHIVED)

    with pytest.raises(InvalidStateTransitionError):
        validate_branch_transition(BranchLifecycleState.ARCHIVED, BranchLifecycleState.ACTIVE)


def test_final_owner_protection_and_scope_invariants() -> None:
    with pytest.raises(BusinessRuleViolationError):
        ensure_not_removing_final_owner(
            active_owner_count=1,
            target_is_active_owner=True,
            new_role="admin",
        )

    with pytest.raises(BusinessRuleViolationError):
        ensure_not_removing_final_owner(
            active_owner_count=1,
            target_is_active_owner=True,
            new_status="revoked",
        )

    # Allowed when >= 2 active owners exist
    ensure_not_removing_final_owner(
        active_owner_count=2,
        target_is_active_owner=True,
        new_role="admin",
    )

    org_a, org_b = uuid4(), uuid4()
    ensure_same_organization_scope(org_a, org_a, "branch")
    with pytest.raises(BusinessRuleViolationError):
        ensure_same_organization_scope(org_a, org_b, "branch")


def test_invitation_acceptance_invariants() -> None:
    now = datetime.now(UTC)
    inv = OrganizationInvitationEntity(
        id=uuid4(),
        organization_id=uuid4(),
        email="chef@example.com",
        role="manager",
        status=InvitationStatus.PENDING,
        expires_at=now + timedelta(days=2),
        created_at=now,
    )
    ensure_invitation_acceptable(inv, now=now, actor_email="CHEF@example.com")

    with pytest.raises(ValidationDomainError):
        ensure_invitation_acceptable(inv, now=now, actor_email="other@example.com")

    with pytest.raises(InvalidStateTransitionError):
        ensure_invitation_acceptable(
            inv, now=now + timedelta(days=3), actor_email="chef@example.com"
        )

    revoked_inv = OrganizationInvitationEntity(
        id=inv.id,
        organization_id=inv.organization_id,
        email=inv.email,
        role="manager",
        status=InvitationStatus.REVOKED,
        expires_at=inv.expires_at,
        created_at=now,
    )
    with pytest.raises(InvalidStateTransitionError):
        ensure_invitation_acceptable(revoked_inv, now=now, actor_email="chef@example.com")


def test_membership_and_branch_assignment_entities() -> None:
    now = datetime.now(UTC)
    m = OrganizationMembershipEntity(
        id=uuid4(),
        organization_id=uuid4(),
        user_id=uuid4(),
        role="owner",
        status="active",
        created_at=now,
        updated_at=now,
    )
    assert m.role == "owner"

    ba = BranchAssignmentEntity(
        id=uuid4(),
        organization_id=m.organization_id,
        restaurant_id=uuid4(),
        branch_id=uuid4(),
        user_id=m.user_id,
        role="branch_manager",
        status="active",
        created_at=now,
        updated_at=now,
    )
    assert ba.role == "branch_manager"
