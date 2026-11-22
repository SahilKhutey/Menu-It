"""
ModularMenu — Unified Infrastructure Database Models Catalog (ARC-06 §3, §4).
Contains all declarative models across identity, tenancy, menus, pricing, presentation,
publishing, media, licensing, and operations.
"""
from app.infrastructure.database.models.identity import (
    PasswordResetTokenModel,
    UserModel,
    UserSessionModel,
)
from app.infrastructure.database.models.licensing import (
    LicenseModel,
    SubscriptionModel,
    SubscriptionPlanModel,
)
from app.infrastructure.database.models.media import (
    MediaAssetModel,
    MediaUsageModel,
)
from app.infrastructure.database.models.menus import (
    MenuCategoryModel,
    MenuItemModel,
    MenuModel,
)
from app.infrastructure.database.models.operations import (
    AuditLogModel,
    IdempotencyRecordModel,
    OutboxEventModel,
)
from app.infrastructure.database.models.organizations import (
    OrganizationInvitationModel,
    OrganizationMemberModel,
    OrganizationModel,
)
from app.infrastructure.database.models.presentation import (
    ComponentDefinitionModel,
    LayoutPresetModel,
    RestaurantDesignConfigModel,
    ThemeModel,
)
from app.infrastructure.database.models.pricing import (
    AddonModel,
    ItemAddonModel,
    ItemPriceModel,
    ItemVariantModel,
    MenuItemTranslationModel,
)
from app.infrastructure.database.models.publishing import (
    DraftRevisionModel,
    MenuVersionModel,
    PublicationActivationModel,
    PublicationModel,
    PublicationSnapshotModel,
    ScheduledPublicationModel,
)
from app.infrastructure.database.models.restaurants import (
    RestaurantDomainModel,
    RestaurantMemberModel,
    RestaurantModel,
    RestaurantSettingsModel,
)

__all__ = [
    "UserModel",
    "UserSessionModel",
    "PasswordResetTokenModel",
    "OrganizationModel",
    "OrganizationMemberModel",
    "OrganizationInvitationModel",
    "RestaurantModel",
    "RestaurantMemberModel",
    "RestaurantSettingsModel",
    "RestaurantDomainModel",
    "MenuModel",
    "MenuCategoryModel",
    "MenuItemModel",
    "ItemPriceModel",
    "ItemVariantModel",
    "AddonModel",
    "ItemAddonModel",
    "MenuItemTranslationModel",
    "ThemeModel",
    "RestaurantDesignConfigModel",
    "LayoutPresetModel",
    "ComponentDefinitionModel",
    "MenuVersionModel",
    "PublicationModel",
    "DraftRevisionModel",
    "PublicationSnapshotModel",
    "PublicationActivationModel",
    "ScheduledPublicationModel",
    "MediaAssetModel",
    "MediaUsageModel",
    "SubscriptionPlanModel",
    "SubscriptionModel",
    "LicenseModel",
    "AuditLogModel",
    "OutboxEventModel",
    "IdempotencyRecordModel",
]
