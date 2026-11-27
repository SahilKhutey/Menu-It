"""Branch domain entities and lifecycle rules (FCD-14 WP-01)."""

from menu_it.domain.branch.entities import BranchEntity, BranchReference
from menu_it.domain.branch.lifecycle import (
    ALLOWED_BRANCH_TRANSITIONS,
    BranchLifecycleState,
    validate_branch_transition,
)

__all__ = [
    "ALLOWED_BRANCH_TRANSITIONS",
    "BranchEntity",
    "BranchLifecycleState",
    "BranchReference",
    "validate_branch_transition",
]
