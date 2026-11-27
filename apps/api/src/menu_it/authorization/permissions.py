"""Permission vocabulary definitions (FCD-05 §13.1, §13.2)."""

import enum


class Permission(enum.StrEnum):
    """Fine-grained permission tokens following resource:action naming standard."""

    # Organization resources
    ORGANIZATION_READ = "organization:read"
    ORGANIZATION_UPDATE = "organization:update"
    ORGANIZATION_SUSPEND = "organization:suspend"
    ORGANIZATION_TRANSFER_OWNERSHIP = "organization:transfer_ownership"
    ORGANIZATION_MANAGE_MEMBERS = "organization:manage_members"

    # Restaurant resources
    RESTAURANT_READ = "restaurant:read"
    RESTAURANT_CREATE = "restaurant:create"
    RESTAURANT_UPDATE = "restaurant:update"
    RESTAURANT_ARCHIVE = "restaurant:archive"

    # Branch resources
    BRANCH_READ = "branch:read"
    BRANCH_CREATE = "branch:create"
    BRANCH_UPDATE = "branch:update"
    BRANCH_MANAGE_ASSIGNMENTS = "branch:manage_assignments"

    # Menu resources
    MENU_READ = "menu:read"
    MENU_CREATE = "menu:create"
    MENU_UPDATE = "menu:update"
    MENU_PUBLISH = "menu:publish"

    # Order resources
    ORDER_READ = "order:read"
    ORDER_CREATE = "order:create"
    ORDER_UPDATE = "order:update"
    ORDER_CANCEL = "order:cancel"

    # Staff resources
    STAFF_READ = "staff:read"
    STAFF_INVITE = "staff:invite"
    STAFF_UPDATE = "staff:update"
    STAFF_REVOKE = "staff:revoke"

    # Billing resources
    BILLING_READ = "billing:read"
    BILLING_MANAGE = "billing:manage"

    # Analytics resources
    ANALYTICS_READ = "analytics:read"

    # Platform administrative resources
    PLATFORM_MANAGE_ORGANIZATIONS = "platform:manage_organizations"
    PLATFORM_MANAGE_USERS = "platform:manage_users"
    PLATFORM_MANAGE_SUPPORT_ACCESS = "platform:manage_support_access"
    PLATFORM_VIEW_AUDIT_LOGS = "platform:view_audit_logs"
