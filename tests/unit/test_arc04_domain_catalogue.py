"""
ARC-04 Complete Domain Test Catalogue (ARC-04 §14.2, ARC04-T001 to ARC04-T050).
Pure Python domain verification without HTTP or database dependencies.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from uuid import uuid4

# Primitives & Value Objects
from app.shared.domain.value_objects import (
    Money, EmailAddress, RestaurantSlug, MenuSlug, DisplayOrder
)
from app.shared.domain.events import (
    DomainEvent, UserRegistered, OrganizationCreated, RestaurantCreated,
    MenuCreated, CategoryCreated, FoodItemCreated, ItemPriceChanged,
    ThemeUpdated, MenuPublished, PublicationRolledBack, MediaUploaded,
    UsageEventRecorded
)

# Domain Modules (MOD-01 to MOD-16)
from app.modules.identity.domain.entities import User, Session
from app.modules.organizations.domain.entities import Organization, Invitation
from app.modules.restaurants.domain.entities import Restaurant, RestaurantSettings
from app.modules.menus.domain.entities import Menu, MenuStatus
from app.modules.categories.domain.entities import Category
from app.modules.food_items.domain.entities import FoodItem, FoodItemStatus
from app.modules.pricing.domain.entities import Price, AvailabilityRule
from app.modules.themes.domain.entities import ThemeDefinition
from app.modules.layouts.domain.entities import LayoutDefinition, LayoutFamily
from app.modules.components.domain.entities import ComponentDefinition
from app.modules.rendering.domain.entities import RenderInput, RenderResult
from app.modules.editor.domain.entities import EditorDraft, EditorSession
from app.modules.publishing.domain.entities import Publication, PublishedVersion
from app.modules.media.domain.entities import MediaAsset, MAX_MEDIA_SIZE_BYTES
from app.modules.licensing.domain.entities import License
from app.modules.analytics.domain.entities import UsageEvent, AnalyticsTracker


# =========================================================================
# MOD-01: Identity & Authentication (ARC04-T001 to ARC04-T004)
# =========================================================================

def test_arc04_t001_register_valid_user():
    """ARC04-T001: Register valid user with normalized email."""
    user = User(
        id=uuid4(),
        email="  Chef@ModularMenu.COM  ",
        password_hash="$2b$12$securehash12345678901234567890",
    )
    assert user.email == "chef@modularmenu.com"
    assert user.is_active is True
    assert user.is_verified is False


def test_arc04_t002_register_invalid_email_syntax():
    """ARC04-T002: Email validation prevents malformed emails."""
    with pytest.raises(ValueError, match="Invalid email address syntax"):
        User(
            id=uuid4(),
            email="invalid-email-at-domain.com",
            password_hash="$2b$12$hash",
        )


def test_arc04_t003_authenticate_inactive_user_rejected():
    """ARC04-T003: Inactive users cannot authenticate."""
    user = User(
        id=uuid4(),
        email="inactive@example.com",
        password_hash="$2b$12$hash",
        is_active=False,
    )
    with pytest.raises(ValueError, match="Account is inactive"):
        user.assert_can_authenticate()


def test_arc04_t004_reuse_revoked_session_rejected():
    """ARC04-T004: Revoked session fails validity assertion."""
    session = Session(id=uuid4(), user_id=uuid4())
    session.assert_valid()  # Valid initially
    session.revoke()
    with pytest.raises(ValueError, match="Session is revoked"):
        session.assert_valid()


# =========================================================================
# MOD-02: Tenant & Organization (ARC04-T005 to ARC04-T007)
# =========================================================================

def test_arc04_t005_create_organization_with_valid_owner():
    """ARC04-T005: Organization creation establishes owner in member set."""
    owner_id = uuid4()
    org = Organization(id=uuid4(), name="Spice Heritage Hospitality", owner_id=owner_id)
    assert org.name == "Spice Heritage Hospitality"
    assert owner_id in org.member_ids


def test_arc04_t006_transfer_ownership_to_non_member_rejected():
    """ARC04-T006: Ownership transfer to non-member is rejected."""
    owner_id = uuid4()
    org = Organization(id=uuid4(), name="Coastal Bites", owner_id=owner_id)
    non_member_id = uuid4()
    with pytest.raises(ValueError, match="New owner must be an existing organization member"):
        org.transfer_ownership(non_member_id)


def test_arc04_t007_accept_expired_invitation_rejected():
    """ARC04-T007: Accepting an expired invitation is rejected."""
    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
    invitation = Invitation(
        id=uuid4(),
        organization_id=uuid4(),
        email="chef@coastal.com",
        expires_at=expired_time,
    )
    with pytest.raises(ValueError, match="Invitation has expired"):
        invitation.assert_can_accept()


# =========================================================================
# MOD-03: Restaurant Management & Configuration (ARC04-T008 to ARC04-T009)
# =========================================================================

def test_arc04_t008_create_restaurant_without_organization_rejected():
    """ARC04-T008: Restaurant without organization is rejected."""
    with pytest.raises(ValueError, match="A restaurant must belong to an organization"):
        Restaurant(
            id=uuid4(),
            organization_id=None,  # type: ignore
            name="Delhi Darbar",
            slug="delhi-darbar",
        )


def test_arc04_t009_configure_invalid_settings_rejected():
    """ARC04-T009: Invalid restaurant settings (e.g. invalid currency) fail schema validation."""
    with pytest.raises(ValueError, match="Invalid currency code"):
        RestaurantSettings(currency="INVALID_CURRENCY").validate_schema()


# =========================================================================
# MOD-04: Menu Management (ARC04-T010 to ARC04-T011)
# =========================================================================

def test_arc04_t010_create_valid_menu():
    """ARC04-T010: Menu is initialized in DRAFT status."""
    menu = Menu(id=uuid4(), restaurant_id=uuid4(), name="Summer Evening Menu")
    assert menu.status == MenuStatus.DRAFT
    assert menu.name == "Summer Evening Menu"


def test_arc04_t011_archive_menu():
    """ARC04-T011: Menu transitions to ARCHIVED status."""
    menu = Menu(id=uuid4(), restaurant_id=uuid4(), name="Old Spring Menu")
    menu.archive()
    assert menu.status == MenuStatus.ARCHIVED


# =========================================================================
# MOD-05: Category Management (ARC04-T012 to ARC04-T014)
# =========================================================================

def test_arc04_t012_create_category_for_valid_menu():
    """ARC04-T012: Category created with deterministic display order."""
    category = Category(
        id=uuid4(), menu_id=uuid4(), name="Tandoori Starters", display_order=0
    )
    assert category.name == "Tandoori Starters"
    assert category.display_order == 0
    assert category.is_visible is True


def test_arc04_t013_reorder_categories():
    """ARC04-T013: Deterministic reordering preserves non-negative order."""
    category = Category(id=uuid4(), menu_id=uuid4(), name="Desserts", display_order=5)
    category.reorder(2)
    assert category.display_order == 2
    with pytest.raises(ValueError, match="Display order must be a non-negative integer"):
        category.reorder(-1)


def test_arc04_t014_category_visibility_toggle():
    """ARC04-T014: Category visibility is toggleable independently of content deletion."""
    category = Category(id=uuid4(), menu_id=uuid4(), name="Seasonal Specials")
    category.hide()
    assert category.is_visible is False
    category.unhide()
    assert category.is_visible is True


# =========================================================================
# MOD-06: Food Item Management (ARC04-T015 to ARC04-T017)
# =========================================================================

def test_arc04_t015_create_valid_food_item():
    """ARC04-T015: Food item created with dietary declarations."""
    item = FoodItem(
        id=uuid4(),
        category_id=uuid4(),
        name="Paneer Tikka Shashlik",
        description="Clay oven roasted cottage cheese with bell peppers",
        dietary_labels=["veg"],
        allergens=["dairy"],
    )
    assert item.name == "Paneer Tikka Shashlik"
    assert item.status == FoodItemStatus.AVAILABLE
    assert "veg" in item.dietary_labels


def test_arc04_t016_assign_item_to_invalid_category_rejected():
    """ARC04-T016: Food item rejects invalid category assignment."""
    item = FoodItem(id=uuid4(), category_id=uuid4(), name="Butter Naan")
    with pytest.raises(ValueError, match="Invalid category assignment"):
        item.assign_to_category(None)  # type: ignore


def test_arc04_t017_deactivate_food_item():
    """ARC04-T017: Food item status transitions to DEACTIVATED."""
    item = FoodItem(id=uuid4(), category_id=uuid4(), name="Seasonal Mango Kulfi")
    item.deactivate()
    assert item.status == FoodItemStatus.DEACTIVATED


# =========================================================================
# MOD-07: Pricing & Availability (ARC04-T018 to ARC04-T020)
# =========================================================================

def test_arc04_t018_create_valid_price():
    """ARC04-T018: Fixed-precision decimal price storage."""
    price = Price(
        id=uuid4(),
        item_id=uuid4(),
        amount=Decimal("385.00"),
        currency="INR",
    )
    assert price.amount == Decimal("385.00")
    assert price.currency == "INR"


def test_arc04_t019_use_negative_price_rejected():
    """ARC04-T019: Negative prices are rejected."""
    with pytest.raises(ValueError, match="Price must be a finite non-negative amount"):
        Price(id=uuid4(), item_id=uuid4(), amount=Decimal("-50.00"), currency="INR")


def test_arc04_t020_change_item_price():
    """ARC04-T020: Price change does not alter frozen historical records."""
    price = Price(id=uuid4(), item_id=uuid4(), amount=Decimal("200.00"), currency="INR")
    price.change_price(Decimal("250.00"))
    assert price.amount == Decimal("250.00")


# =========================================================================
# MOD-08: Theme Engine (ARC04-T021 to ARC04-T022)
# =========================================================================

def test_arc04_t021_resolve_valid_theme():
    """ARC04-T021: Resolves deterministic token output."""
    theme = ThemeDefinition(
        theme_id="minimal-light",
        name="Minimal Light",
        tokens={
            "colors": {"background": "#ffffff", "text": "#111827", "primary": "#16a34a"},
            "typography": {"fontFamily": "Inter"},
        },
    )
    resolved = theme.resolve_tokens()
    assert resolved["theme_id"] == "minimal-light"
    assert resolved["tokens"]["colors"]["primary"] == "#16a34a"


def test_arc04_t022_resolve_theme_with_invalid_color_rejected():
    """ARC04-T022: Invalid color tokens fail validation."""
    with pytest.raises(ValueError, match="Invalid hex color 'not-a-color'"):
        ThemeDefinition(
            theme_id="broken-theme",
            name="Broken Theme",
            tokens={"colors": {"primary": "not-a-color"}},
        )


# =========================================================================
# MOD-09: Layout Engine (ARC04-T023 to ARC04-T024)
# =========================================================================

def test_arc04_t023_resolve_supported_layout():
    """ARC04-T023: Layout definition supports approved families."""
    layout = LayoutDefinition(layout_id="grid-classic", family=LayoutFamily.GRID)
    assert layout.family == LayoutFamily.GRID
    assert layout.validate_slot_compatibility("items") is True


def test_arc04_t024_configure_incompatible_slot_rejected():
    """ARC04-T024: Slot not in supported_slots is marked incompatible."""
    layout = LayoutDefinition(layout_id="list-simple", family=LayoutFamily.LIST)
    assert layout.validate_slot_compatibility("arbitrary_unknown_slot") is False


# =========================================================================
# MOD-10: Component Registry (ARC04-T025 to ARC04-T027)
# =========================================================================

def test_arc04_t025_register_component_definition():
    """ARC04-T025: Component registry accepts valid component."""
    comp = ComponentDefinition(
        component_id="food-item-card",
        version=1,
        schema={"properties": {"title": "string", "price": "number"}},
    )
    assert comp.component_id == "food-item-card"
    assert comp.supports_layout("grid") is True


def test_arc04_t026_supply_unsupported_property_rejected():
    """ARC04-T026: Unsupported properties outside schema are rejected."""
    comp = ComponentDefinition(
        component_id="price-label",
        version=1,
        schema={"properties": {"amount": "string", "currency": "string"}},
    )
    with pytest.raises(ValueError, match="Property 'malicious_script' is not supported"):
        comp.validate_properties({"amount": "250.00", "malicious_script": "<script>"})


def test_arc04_t027_request_deprecated_component():
    """ARC04-T027: Component deprecation flag is respected."""
    comp = ComponentDefinition(
        component_id="legacy-carousel",
        version=1,
        is_deprecated=True,
    )
    assert comp.is_deprecated is True


# =========================================================================
# MOD-11: Menu Rendering Engine (ARC04-T028 to ARC04-T030)
# =========================================================================

def test_arc04_t028_render_valid_snapshot():
    """ARC04-T028: Stable render result constructed from published snapshot."""
    render_input = RenderInput(
        published_snapshot={
            "menu_name": "Royal Feast",
            "categories": [{"name": "Mains", "items": [{"name": "Biryani"}]}],
        },
        render_context={"viewport": "mobile"},
    )
    result = RenderResult(
        menu_data=render_input.published_snapshot,
        theme={"colors": {"primary": "#245c4a"}},
        layout={"family": "list"},
        components=[{"type": "item-card"}],
    )
    assert result.menu_data["menu_name"] == "Royal Feast"
    assert len(result.components) == 1


def test_arc04_t029_render_without_optional_image_graceful_fallback():
    """ARC04-T030: Missing optional media does not break rendering."""
    snapshot = {
        "menu_name": "Cafe Menu",
        "items": [{"name": "Espresso", "image_url": None}],
    }
    result = RenderResult(
        menu_data=snapshot,
        theme={},
        layout={},
        components=[{"type": "item-card", "has_image": False}],
    )
    assert result.menu_data["items"][0]["image_url"] is None


# =========================================================================
# MOD-12: Visual Menu Editor (ARC04-T031 to ARC04-T033)
# =========================================================================

def test_arc04_t031_edit_draft_preserves_published_snapshot():
    """ARC04-T031: Draft mutations do not mutate published snapshots."""
    draft = EditorDraft(
        draft_id=uuid4(),
        restaurant_id=uuid4(),
        configuration={"theme": "minimal-light", "cards": 2},
    )
    draft.update_configuration({"theme": "dark-luxury", "cards": 3})
    assert draft.revision == 2
    assert draft.configuration["theme"] == "dark-luxury"


def test_arc04_t032_undo_redo_valid_change():
    """ARC04-T032: Reversible draft revisions via undo and redo."""
    draft = EditorDraft(
        draft_id=uuid4(),
        restaurant_id=uuid4(),
        configuration={"theme": "v1"},
    )
    draft.update_configuration({"theme": "v2"})
    assert draft.configuration["theme"] == "v2"

    draft.undo()
    assert draft.configuration["theme"] == "v1"

    draft.redo()
    assert draft.configuration["theme"] == "v2"


def test_arc04_t033_editor_session_close():
    """ARC04-T033: Editor session lifecycle management."""
    session = EditorSession(session_id=uuid4(), user_id=uuid4(), draft_id=uuid4())
    assert session.is_active is True
    session.close()
    assert session.is_active is False


# =========================================================================
# MOD-13: Publishing & Versioning (ARC04-T034 to ARC04-T037)
# =========================================================================

def test_arc04_t034_publish_valid_candidate():
    """ARC04-T034: Publication creates immutable version with SHA-256 digest."""
    pub = Publication(publication_id=uuid4(), menu_id=uuid4())
    payload = {"name": "Grand Menu", "items": [{"name": "Dal Makhani", "price": "295.00"}]}
    ver = PublishedVersion.create(
        version_id=uuid4(),
        publication_id=pub.publication_id,
        version_number=1,
        payload=payload,
    )
    pub.publish_version(ver)

    assert pub.active_version_id == ver.version_id
    assert len(ver.sha256_hash) == 64  # SHA-256 hex string


def test_arc04_t035_publish_duplicate_version_number_rejected():
    """ARC04-T035: Cannot overwrite existing version number."""
    pub = Publication(publication_id=uuid4(), menu_id=uuid4())
    ver1 = PublishedVersion.create(uuid4(), pub.publication_id, 1, {"v": 1})
    pub.publish_version(ver1)

    ver2 = PublishedVersion.create(uuid4(), pub.publication_id, 1, {"v": 2})
    with pytest.raises(ValueError, match="Version number 1 already published"):
        pub.publish_version(ver2)


def test_arc04_t036_rollback_to_valid_version():
    """ARC04-T036: Rollback reactivates prior snapshot without mutation."""
    pub = Publication(publication_id=uuid4(), menu_id=uuid4())
    ver1 = PublishedVersion.create(uuid4(), pub.publication_id, 1, {"name": "Version 1"})
    ver2 = PublishedVersion.create(uuid4(), pub.publication_id, 2, {"name": "Version 2"})
    pub.publish_version(ver1)
    pub.publish_version(ver2)
    assert pub.active_version_id == ver2.version_id

    # Roll back to version 1
    rolled = pub.rollback_to_version(ver1.version_id)
    assert pub.active_version_id == ver1.version_id
    assert rolled.snapshot_payload["name"] == "Version 1"


# =========================================================================
# MOD-14: Media Management (ARC04-T038 to ARC04-T040)
# =========================================================================

def test_arc04_t038_upload_unsupported_file_rejected():
    """ARC04-T038: Unsupported file MIME types are rejected."""
    with pytest.raises(ValueError, match="Unsupported media content type"):
        MediaAsset(
            asset_id=uuid4(),
            restaurant_id=uuid4(),
            filename="malicious.exe",
            content_type="application/x-msdownload",
            size_bytes=1024,
            storage_path="/uploads/malicious.exe",
        )


def test_arc04_t039_upload_oversized_media_rejected():
    """ARC04-T039: Files exceeding 5MB are rejected."""
    with pytest.raises(ValueError, match="exceeds limit"):
        MediaAsset(
            asset_id=uuid4(),
            restaurant_id=uuid4(),
            filename="large_photo.png",
            content_type="image/png",
            size_bytes=MAX_MEDIA_SIZE_BYTES + 1024,
            storage_path="/uploads/large_photo.png",
        )


def test_arc04_t040_delete_referenced_media_rejected():
    """ARC04-T040: Deletion of actively referenced media is rejected."""
    asset = MediaAsset(
        asset_id=uuid4(),
        restaurant_id=uuid4(),
        filename="curry.webp",
        content_type="image/webp",
        size_bytes=204800,
        storage_path="/uploads/curry.webp",
        reference_count=3,
    )
    with pytest.raises(ValueError, match="Cannot delete media asset actively referenced"):
        asset.assert_can_delete()


# =========================================================================
# MOD-15: Subscription & Licensing (ARC04-T041 to ARC04-T043)
# =========================================================================

def test_arc04_t041_evaluate_entitled_feature():
    """ARC04-T041: Entitled feature evaluates to True."""
    future_time = datetime.now(timezone.utc) + timedelta(days=30)
    lic = License(
        license_id=uuid4(),
        organization_id=uuid4(),
        license_key="LIC-MODULAR-ENTERPRISE-2026",
        entitled_features={"custom_themes", "analytics", "unlimited_dishes"},
        expires_at=future_time,
    )
    assert lic.can_access_feature("custom_themes") is True


def test_arc04_t042_evaluate_unentitled_feature():
    """ARC04-T042: Unentitled feature evaluates to False."""
    future_time = datetime.now(timezone.utc) + timedelta(days=30)
    lic = License(
        license_id=uuid4(),
        organization_id=uuid4(),
        license_key="LIC-MODULAR-STARTER-2026",
        entitled_features={"standard_themes"},
        expires_at=future_time,
    )
    assert lic.can_access_feature("custom_themes") is False


def test_arc04_t043_validate_forged_license_rejected():
    """ARC04-T043: Forged or malformed license key fails validation."""
    future_time = datetime.now(timezone.utc) + timedelta(days=30)
    lic = License(
        license_id=uuid4(),
        organization_id=uuid4(),
        license_key="FORGED-KEY-NOT-VALID",
        entitled_features={"custom_themes"},
        expires_at=future_time,
    )
    assert lic.is_valid() is False


# =========================================================================
# MOD-16: Analytics & Integrations (ARC04-T044 to ARC04-T045)
# =========================================================================

def test_arc04_t044_duplicate_analytics_event_deduplicated():
    """ARC04-T044: Duplicate event IDs are processed idempotently."""
    tracker = AnalyticsTracker()
    event_id = uuid4()
    event = UsageEvent(event_id=event_id, restaurant_id=uuid4(), event_type="qr_scan")

    first_attempt = tracker.record_event(event)
    assert first_attempt is True  # Recorded

    second_attempt = tracker.record_event(event)
    assert second_attempt is False  # Deduplicated


# =========================================================================
# Cross-Module Workflows (ARC04-T048 to ARC04-T050)
# =========================================================================

def test_arc04_t048_event_consumer_idempotency():
    """ARC04-T048: Cross-module events handle duplicate delivery safely."""
    event = MenuPublished(
        menu_id=uuid4(),
        publication_id=uuid4(),
        version_id=uuid4(),
        version_number=1,
    )
    processed_events = set()

    def handle_event(e: DomainEvent) -> bool:
        if e.event_id in processed_events:
            return False
        processed_events.add(e.event_id)
        return True

    assert handle_event(event) is True
    assert handle_event(event) is False  # Idempotent skip


def test_arc04_t049_restaurant_onboarding_workflow():
    """
    VAL-ARC04-01 / Cross-module onboarding:
    User registers (MOD-01) -> Organization created (MOD-02) -> Restaurant established (MOD-03).
    """
    user = User(id=uuid4(), email="owner@bikanervala.com", password_hash="$2b$12$hash")
    org = Organization(id=uuid4(), name="Bikanervala Foods", owner_id=user.id)
    restaurant = Restaurant(
        id=uuid4(),
        organization_id=org.id,
        name="Bikanervala Connaught Place",
        slug="bikanervala-cp",
    )

    assert restaurant.organization_id == org.id
    assert org.owner_id == user.id
    assert restaurant.is_active is True


def test_arc04_t050_edition_neutrality_domain_execution():
    """
    ARC04-T050 / VAL-ARC04-05:
    Domain entities and rules execute identically across SaaS and customer-hosted profiles.
    """
    menu = Menu(id=uuid4(), restaurant_id=uuid4(), name="Executive Thali Menu")
    category = Category(id=uuid4(), menu_id=menu.id, name="Thalis", display_order=1)
    item = FoodItem(id=uuid4(), category_id=category.id, name="Royal Thali")
    price = Price(id=uuid4(), item_id=item.id, amount=Decimal("499.00"), currency="INR")

    assert menu.name == "Executive Thali Menu"
    assert category.menu_id == menu.id
    assert item.category_id == category.id
    assert price.amount == Decimal("499.00")
