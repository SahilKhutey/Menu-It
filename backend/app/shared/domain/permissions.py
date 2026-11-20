"""
ModularMenu — Domain Permission Vocabulary (ARC-05 §5.5).
Defines fine-grained permission identifiers governing multi-tenant access control.
"""
from enum import StrEnum


class Permission(StrEnum):
    # Organization Management (MOD-02)
    ORGANIZATION_READ = "organization.read"
    ORGANIZATION_UPDATE = "organization.update"
    ORGANIZATION_DELETE = "organization.delete"
    MEMBER_INVITE = "organization.member.invite"
    MEMBER_REMOVE = "organization.member.remove"
    MEMBER_ROLE_UPDATE = "organization.member.role_update"

    # Restaurant / Branch Management (MOD-03)
    RESTAURANT_CREATE = "restaurant.create"
    RESTAURANT_READ = "restaurant.read"
    RESTAURANT_UPDATE = "restaurant.update"
    RESTAURANT_DELETE = "restaurant.delete"

    # Menu Management (MOD-04, MOD-05, MOD-06, MOD-07)
    MENU_CREATE = "menu.create"
    MENU_READ = "menu.read"
    MENU_UPDATE = "menu.update"
    MENU_DELETE = "menu.delete"
    MENU_PUBLISH = "menu.publish"
    MENU_ROLLBACK = "menu.rollback"

    CATEGORY_MANAGE = "category.manage"
    FOOD_ITEM_MANAGE = "food_item.manage"
    PRICING_MANAGE = "pricing.manage"
    AVAILABILITY_MANAGE = "availability.manage"

    # Theme & Visual Styling (MOD-08, MOD-09)
    THEME_READ = "theme.read"
    THEME_UPDATE = "theme.update"
    LAYOUT_UPDATE = "layout.update"

    # Visual Studio / Drafts (MOD-12)
    EDITOR_DRAFT_READ = "editor.draft.read"
    EDITOR_DRAFT_WRITE = "editor.draft.write"

    # Media Storage & Assets (MOD-14)
    MEDIA_UPLOAD = "media.upload"
    MEDIA_READ_PRIVATE = "media.read_private"
    MEDIA_DELETE = "media.delete"

    # Subscription & Entitlements (MOD-16)
    SUBSCRIPTION_READ = "subscription.read"
    SUBSCRIPTION_MANAGE = "subscription.manage"

    # Audit & Compliance
    AUDIT_READ = "audit.read"
