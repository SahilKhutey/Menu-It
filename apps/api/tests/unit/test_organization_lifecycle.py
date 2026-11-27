"""Unit tests for organization lifecycle transitions (FCD-04 §14, §18.7)."""

import pytest

from menu_it.database.models.organization import (
    Organization,
    OrganizationStatus,
)
from menu_it.services.organization_lifecycle import (
    InvalidOrganizationTransition,
    transition_organization,
)


def test_provisioning_can_be_activated():
    """Verify organization transitions from PROVISIONING to ACTIVE."""
    org = Organization(
        name="Demo Corp",
        slug="demo-corp",
        status=OrganizationStatus.PROVISIONING,
    )
    result = transition_organization(org, OrganizationStatus.ACTIVE)
    assert result == OrganizationStatus.ACTIVE
    assert org.status == OrganizationStatus.ACTIVE


def test_active_to_suspended_and_back():
    """Verify ACTIVE -> SUSPENDED -> ACTIVE state cycle."""
    org = Organization(
        name="Suspension Test",
        slug="suspension-test",
        status=OrganizationStatus.ACTIVE,
    )
    transition_organization(org, OrganizationStatus.SUSPENDED)
    assert org.status == OrganizationStatus.SUSPENDED

    transition_organization(org, OrganizationStatus.ACTIVE)
    assert org.status == OrganizationStatus.ACTIVE


def test_offboarding_and_deactivation():
    """Verify ACTIVE -> OFFBOARDING -> DEACTIVATED terminal progression."""
    org = Organization(
        name="Exit Test",
        slug="exit-test",
        status=OrganizationStatus.ACTIVE,
    )
    transition_organization(org, OrganizationStatus.OFFBOARDING)
    assert org.status == OrganizationStatus.OFFBOARDING

    transition_organization(org, OrganizationStatus.DEACTIVATED)
    assert org.status == OrganizationStatus.DEACTIVATED


def test_deactivated_is_terminal():
    """Verify no transitions are permitted from DEACTIVATED state."""
    org = Organization(
        name="Terminal Test",
        slug="terminal-test",
        status=OrganizationStatus.DEACTIVATED,
    )
    with pytest.raises(InvalidOrganizationTransition):
        transition_organization(org, OrganizationStatus.ACTIVE)


def test_illegal_transitions_rejected():
    """Verify direct illegal jumps are rejected with InvalidOrganizationTransition."""
    org = Organization(
        name="Illegal Jump",
        slug="illegal-jump",
        status=OrganizationStatus.PROVISIONING,
    )
    # Cannot jump directly from PROVISIONING to SUSPENDED or OFFBOARDING
    with pytest.raises(InvalidOrganizationTransition):
        transition_organization(org, OrganizationStatus.SUSPENDED)

    with pytest.raises(InvalidOrganizationTransition):
        transition_organization(org, OrganizationStatus.OFFBOARDING)
