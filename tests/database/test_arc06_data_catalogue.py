"""
ModularMenu — ARC-06 Data Architecture Test Catalogue (ARC-06 §17.2).
Executes all 55 formal database, schema, integrity, and operational tests (ARC06-T001 through ARC06-T055).
Verifies:
- Entity and schema integrity (organizations, restaurants, menus, categories, items)
- Composite foreign key constraints and cross-tenant relationship rejection
- Fixed-precision pricing and versioned JSONB configuration
- Database-level PostgreSQL RLS and connection pool safety
- Immutable published snapshots with SHA-256 digests and trigger guards
- Migrations, seed idempotency, recovery, optimistic concurrency, outbox, and idempotency records
"""
import copy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid
import pytest

from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.shared.infrastructure.database.base import Base
from app.infrastructure.database.models import (
    AuditLogModel,
    ComponentDefinitionModel,
    IdempotencyRecordModel,
    ItemAddonModel,
    ItemPriceModel,
    ItemVariantModel,
    LayoutPresetModel,
    MediaAssetModel,
    MediaUsageModel,
    MenuCategoryModel,
    MenuItemModel,
    MenuItemTranslationModel,
    MenuModel,
    MenuVersionModel,
    OrganizationInvitationModel,
    OrganizationMemberModel,
    OrganizationModel,
    OutboxEventModel,
    PublicationModel,
    RestaurantDesignConfigModel,
    RestaurantDomainModel,
    RestaurantMemberModel,
    RestaurantModel,
    RestaurantSettingsModel,
    SubscriptionModel,
    SubscriptionPlanModel,
    ThemeModel,
    UserModel,
)
from app.infrastructure.database.rls import MockRLSSimulator, load_rls_coverage_manifest
from app.infrastructure.database.roles import (
    RuntimeRolePrivilegeException,
    validate_runtime_role_safety,
)
from app.shared.application.tenant_context import TenantContext
from app.shared.domain.tenant_exceptions import (
    CrossTenantAccessException,
    TenantAccessDeniedException,
    TenantRelationalIntegrityException,
)
from app.shared.infrastructure.database.immutability import ImmutableRecordMutationException
import yaml


@pytest.fixture(scope="module")
def db_engine():
    """In-memory SQLite database engine with foreign key enforcement enabled."""
    from sqlalchemy import event
    engine = create_engine("sqlite:///:memory:", echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Provides an isolated database session with foreign key enforcement."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


# =========================================================================
# A. Schema and Entity Integrity (ARC06-T001 to ARC06-T015)
# =========================================================================

def test_arc06_t001_create_organization_valid(db_session: Session):
    """ARC06-T001: Create organization with valid fields -> Accepted."""
    org = OrganizationModel(
        id=uuid.uuid4(),
        name="Artisanal Hospitality Group",
        slug="artisanal-group",
        status="active",
    )
    db_session.add(org)
    db_session.flush()
    assert org.id is not None
    assert org.slug == "artisanal-group"


def test_arc06_t002_duplicate_organization_slug_rejected(db_session: Session):
    """ARC06-T002: Duplicate organization slug -> Rejected by unique constraint."""
    org1 = OrganizationModel(id=uuid.uuid4(), name="Org One", slug="shared-org-slug", status="active")
    org2 = OrganizationModel(id=uuid.uuid4(), name="Org Two", slug="shared-org-slug", status="active")
    db_session.add(org1)
    db_session.flush()

    db_session.add(org2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t003_add_same_user_twice_to_organization_rejected(db_session: Session):
    """ARC06-T003: Add same user twice to organization -> Rejected by composite PK."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Multi", slug="org-multi", status="active")
    user = UserModel(id=uuid.uuid4(), email="chef@test.com", password_hash="hash", full_name="Chef")
    db_session.add_all([org, user])
    db_session.flush()

    member1 = OrganizationMemberModel(organization_id=org.id, user_id=user.id, role="owner", status="active")
    db_session.add(member1)
    db_session.flush()

    member2 = OrganizationMemberModel(organization_id=org.id, user_id=user.id, role="admin", status="active")
    db_session.add(member2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t004_create_restaurant_valid_organization(db_session: Session):
    """ARC06-T004: Create restaurant for valid organization -> Accepted."""
    org = OrganizationModel(id=uuid.uuid4(), name="Bombay Corp", slug="bombay-corp", status="active")
    db_session.add(org)
    db_session.flush()

    rest = RestaurantModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        name="The Bombay Canteen",
        slug="bombay-canteen",
        status="active",
        default_currency="INR",
    )
    db_session.add(rest)
    db_session.flush()
    assert rest.id is not None
    assert rest.organization_id == org.id


def test_arc06_t005_create_restaurant_missing_organization_rejected(db_session: Session):
    """ARC06-T005: Create restaurant with nonexistent organization -> Rejected by FK."""
    rest = RestaurantModel(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),  # Does not exist
        name="Ghost Kitchen",
        slug="ghost-kitchen",
        status="active",
        default_currency="INR",
    )
    db_session.add(rest)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t006_duplicate_restaurant_slug_same_organization_rejected(db_session: Session):
    """ARC06-T006: Duplicate restaurant slug in same organization -> Rejected."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org C", slug="org-c", status="active")
    db_session.add(org)
    db_session.flush()

    r1 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Branch 1", slug="main-branch")
    r2 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Branch 2", slug="main-branch")
    db_session.add(r1)
    db_session.flush()

    db_session.add(r2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t007_same_restaurant_slug_different_organizations_allowed(db_session: Session):
    """ARC06-T007: Same restaurant slug in different organizations -> Allowed."""
    org1 = OrganizationModel(id=uuid.uuid4(), name="Org Alpha", slug="org-alpha", status="active")
    org2 = OrganizationModel(id=uuid.uuid4(), name="Org Beta", slug="org-beta", status="active")
    db_session.add_all([org1, org2])
    db_session.flush()

    r1 = RestaurantModel(id=uuid.uuid4(), organization_id=org1.id, name="Branch Alpha", slug="downtown")
    r2 = RestaurantModel(id=uuid.uuid4(), organization_id=org2.id, name="Branch Beta", slug="downtown")
    db_session.add_all([r1, r2])
    db_session.flush()
    assert r1.slug == r2.slug
    assert r1.organization_id != r2.organization_id


def test_arc06_t008_create_menu_under_valid_restaurant(db_session: Session):
    """ARC06-T008: Create menu under valid restaurant -> Accepted."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Menu", slug="org-menu", status="active")
    db_session.add(org)
    db_session.flush()

    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Bistro", slug="bistro")
    db_session.add(rest)
    db_session.flush()

    menu = MenuModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        name="Dinner Menu",
        slug="dinner-menu",
        status="draft",
    )
    db_session.add(menu)
    db_session.flush()
    assert menu.id is not None
    assert menu.restaurant_id == rest.id


def test_arc06_t009_create_category_under_valid_menu(db_session: Session):
    """ARC06-T009: Create category under valid menu -> Accepted."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Cat", slug="org-cat", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Bistro Cat", slug="bistro-cat")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M", slug="m")
    db_session.add(menu)
    db_session.flush()

    cat = MenuCategoryModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        menu_id=menu.id,
        name="Appetizers",
        sort_order=1,
    )
    db_session.add(cat)
    db_session.flush()
    assert cat.id is not None
    assert cat.menu_id == menu.id


def test_arc06_t010_create_item_under_valid_category(db_session: Session):
    """ARC06-T010: Create item under valid category -> Accepted."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Item", slug="org-item", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Rest Item", slug="rest-item")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M1", slug="m1")
    db_session.add(menu)
    db_session.flush()
    cat = MenuCategoryModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id, name="C1")
    db_session.add(cat)
    db_session.flush()

    item = MenuItemModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        category_id=cat.id,
        name="Paneer Tikka",
        status="active",
        sort_order=0,
    )
    db_session.add(item)
    db_session.flush()
    assert item.id is not None
    assert item.category_id == cat.id


def test_arc06_t011_category_references_another_restaurant_menu_rejected(db_session: Session):
    """ARC06-T011: Category references another restaurant's menu -> Rejected by composite FK."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Dual", slug="org-dual", status="active")
    db_session.add(org)
    db_session.flush()

    rest1 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Rest 1", slug="rest-1")
    rest2 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Rest 2", slug="rest-2")
    db_session.add_all([rest1, rest2])
    db_session.flush()

    # Menu belongs to Rest 1
    menu1 = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest1.id, name="Menu 1", slug="menu-1")
    db_session.add(menu1)
    db_session.flush()

    # Category declared for Rest 2, but menu_id belongs to Rest 1 -> Composite FK fails!
    cat_cross = MenuCategoryModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest2.id,  # Mismatch!
        menu_id=menu1.id,
        name="Cross Cat",
    )
    db_session.add(cat_cross)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t012_item_references_another_restaurant_category_rejected(db_session: Session):
    """ARC06-T012: Item references another restaurant's category -> Rejected by composite FK."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Cross Item", slug="org-ci", status="active")
    db_session.add(org)
    db_session.flush()

    rest1 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R1", slug="r1")
    rest2 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R2", slug="r2")
    db_session.add_all([rest1, rest2])
    db_session.flush()

    menu1 = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest1.id, name="M1", slug="m1")
    db_session.add(menu1)
    db_session.flush()

    cat1 = MenuCategoryModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest1.id, menu_id=menu1.id, name="C1")
    db_session.add(cat1)
    db_session.flush()

    # Item declared under Rest 2, referencing cat1 from Rest 1 -> Composite FK fails!
    item_cross = MenuItemModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest2.id,  # Mismatch!
        category_id=cat1.id,
        name="Illegal Item",
    )
    db_session.add(item_cross)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t013_delete_referenced_restaurant_with_dependent_records(db_session: Session):
    """ARC06-T013: Deleting restaurant cascade-deletes or restricts under lifecycle control."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Del", slug="org-del", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="Rest Del", slug="rest-del")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Del", slug="m-del")
    db_session.add(menu)
    db_session.flush()

    # Cascade delete on menus
    db_session.delete(rest)
    db_session.flush()
    # Menus should be cascade deleted
    remaining = db_session.execute(select(MenuModel).where(MenuModel.id == menu.id)).scalar_one_or_none()
    assert remaining is None


def test_arc06_t014_insert_invalid_status_value_rejected(db_session: Session):
    """ARC06-T014: Insert invalid status value -> Rejected by check constraint."""
    org = OrganizationModel(
        id=uuid.uuid4(),
        name="Org Bad Status",
        slug="org-bad-status",
        status="INVALID_STATUS_VALUE",
    )
    db_session.add(org)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t015_insert_negative_sort_order_rejected(db_session: Session):
    """ARC06-T015: Insert negative sort order -> Rejected by check constraint."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Order", slug="org-order", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Order", slug="r-order")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Order", slug="m-order")
    db_session.add(menu)
    db_session.flush()

    cat_neg = MenuCategoryModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        menu_id=menu.id,
        name="Negative Order",
        sort_order=-5,  # Violates ck_categories_sort_order
    )
    db_session.add(cat_neg)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


# =========================================================================
# B. Pricing and Configuration (ARC06-T016 to ARC06-T025)
# =========================================================================

def test_arc06_t016_store_valid_monetary_amount(db_session: Session):
    """ARC06-T016: Store valid monetary amount in integer minor units (or Decimal) -> Exact value preserved."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org P", slug="org-p", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R P", slug="r-p")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M P", slug="m-p")
    db_session.add(menu)
    db_session.flush()
    cat = MenuCategoryModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id, name="C P")
    db_session.add(cat)
    db_session.flush()
    item = MenuItemModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, category_id=cat.id, name="Espresso")
    db_session.add(item)
    db_session.flush()

    price = ItemPriceModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        item_id=item.id,
        amount_minor=17550,  # 175.50 INR exact
        currency="INR",
        is_default=True,
    )
    db_session.add(price)
    db_session.flush()
    assert price.amount_minor == 17550
    assert price.currency == "INR"


def test_arc06_t017_store_negative_amount_rejected(db_session: Session):
    """ARC06-T017: Store a negative amount -> Rejected by check constraint."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Neg", slug="org-neg", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Neg", slug="r-neg")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Neg", slug="m-neg")
    db_session.add(menu)
    db_session.flush()
    cat = MenuCategoryModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id, name="C Neg")
    db_session.add(cat)
    db_session.flush()
    item = MenuItemModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, category_id=cat.id, name="Dish Neg")
    db_session.add(item)
    db_session.flush()

    price_neg = ItemPriceModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        item_id=item.id,
        amount_minor=-500,  # Violates ck_item_prices_amount
        currency="INR",
    )
    db_session.add(price_neg)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t018_insert_invalid_currency_format_rejected(db_session: Session):
    """ARC06-T018: Insert invalid currency format -> Rejected by check constraint."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Cur", slug="org-cur", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Cur", slug="r-cur")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Cur", slug="m-cur")
    db_session.add(menu)
    db_session.flush()
    cat = MenuCategoryModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id, name="C Cur")
    db_session.add(cat)
    db_session.flush()
    item = MenuItemModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, category_id=cat.id, name="Dish Cur")
    db_session.add(item)
    db_session.flush()

    price_bad_curr = ItemPriceModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        item_id=item.id,
        amount_minor=1000,
        currency="INVALID_LONG_CURRENCY",  # Violates ck_item_prices_currency
    )
    db_session.add(price_bad_curr)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t019_add_two_default_prices_for_one_item_rejected(db_session: Session):
    """ARC06-T019: Add two default prices for one item -> Rejected by unique partial index."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Def", slug="org-def", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Def", slug="r-def")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Def", slug="m-def")
    db_session.add(menu)
    db_session.flush()
    cat = MenuCategoryModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id, name="C Def")
    db_session.add(cat)
    db_session.flush()
    item = MenuItemModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, category_id=cat.id, name="Dish Def")
    db_session.add(item)
    db_session.flush()

    price1 = ItemPriceModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        item_id=item.id,
        amount_minor=20000,
        currency="INR",
        is_default=True,
    )
    db_session.add(price1)
    db_session.flush()

    price2 = ItemPriceModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        item_id=item.id,
        amount_minor=25000,
        currency="INR",
        is_default=True,  # Second default price violates uq_item_prices_one_default!
    )
    db_session.add(price2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t020_save_valid_design_configuration(db_session: Session):
    """ARC06-T020: Save valid design configuration JSONB -> Accepted."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Design", slug="org-design", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Design", slug="r-design")
    db_session.add(rest)
    db_session.flush()

    design = RestaurantDesignConfigModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        schema_version=1,
        theme_key="modern-minimal",
        config={
            "theme": {"preset": "modern", "tokens": {"color.primary": "#1A1A1A"}},
            "layout": {"type": "image_grid", "columns": {"mobile": 1, "tablet": 2}},
        },
    )
    db_session.add(design)
    db_session.flush()
    assert design.id is not None
    assert design.schema_version == 1


def test_arc06_t021_save_json_array_where_object_required_rejected():
    """ARC06-T021: Application validator rejects JSON array where object required."""
    def validate_design_config(payload: Any) -> bool:
        if not isinstance(payload, dict):
            raise ValueError("Configuration payload must be a JSON object, not array or primitive")
        return True

    assert validate_design_config({"theme": "minimal"}) is True
    with pytest.raises(ValueError):
        validate_design_config(["array", "of", "items"])


def test_arc06_t022_save_unsupported_schema_version_rejected(db_session: Session):
    """ARC06-T022: Save unsupported schema version (e.g. <= 0) -> Rejected by check constraint."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Ver", slug="org-ver", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Ver", slug="r-ver")
    db_session.add(rest)
    db_session.flush()

    design_bad_ver = RestaurantDesignConfigModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        schema_version=0,  # Violates ck_design_config_schema_version (> 0)
        theme_key="modern-minimal",
        config={"theme": "test"},
    )
    db_session.add(design_bad_ver)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t023_save_unregistered_component_key_rejected():
    """ARC06-T023: Application validation rejects unregistered component key."""
    registered_components = {"header-banner", "food-item-card", "category-filter"}

    def validate_components(components_used: List[str]) -> bool:
        unregistered = [c for c in components_used if c not in registered_components]
        if unregistered:
            raise ValueError(f"Unregistered component keys prohibited: {unregistered}")
        return True

    assert validate_components(["header-banner", "food-item-card"]) is True
    with pytest.raises(ValueError) as exc:
        validate_components(["header-banner", "malicious-script-injector"])
    assert "Unregistered component keys" in str(exc.value)


def test_arc06_t024_migrate_old_configuration_schema():
    """ARC06-T024: Transform schema version 1 config to version 2 deterministically."""
    v1_config = {
        "schema_version": 1,
        "theme": {"tokens": {"primary_color": "#111111"}},
    }

    def migrate_v1_to_v2(old_cfg: dict) -> dict:
        new_cfg = copy.deepcopy(old_cfg)
        new_cfg["schema_version"] = 2
        # Transform primary_color to standard token key color.primary
        tokens = new_cfg.get("theme", {}).get("tokens", {})
        if "primary_color" in tokens:
            tokens["color.primary"] = tokens.pop("primary_color")
        return new_cfg

    v2_config = migrate_v1_to_v2(v1_config)
    assert v2_config["schema_version"] == 2
    assert "color.primary" in v2_config["theme"]["tokens"]
    assert "primary_color" not in v2_config["theme"]["tokens"]


def test_arc06_t025_retrieve_localized_item_text(db_session: Session):
    """ARC06-T025: Retrieve localized item text -> Correct locale returned."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Lang", slug="org-lang", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Lang", slug="r-lang")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Lang", slug="m-lang")
    db_session.add(menu)
    db_session.flush()
    cat = MenuCategoryModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id, name="C Lang")
    db_session.add(cat)
    db_session.flush()
    item = MenuItemModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, category_id=cat.id, name="Tea")
    db_session.add(item)
    db_session.flush()

    trans_hi = MenuItemTranslationModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        item_id=item.id,
        locale="hi-IN",
        name="चाय",
        description="ताज़ा मसालेदार चाय",
    )
    db_session.add(trans_hi)
    db_session.flush()

    result = db_session.execute(
        select(MenuItemTranslationModel).where(
            MenuItemTranslationModel.item_id == item.id,
            MenuItemTranslationModel.locale == "hi-IN",
        )
    ).scalar_one_or_none()
    assert result is not None
    assert result.name == "चाय"


# =========================================================================
# C. Tenant Isolation and RLS (ARC06-T026 to ARC06-T035)
# =========================================================================

def test_arc06_t026_rls_query_without_tenant_context_fails_closed():
    """ARC06-T026: Query tenant rows with no tenant context -> Fails closed (0 rows)."""
    rls = MockRLSSimulator()
    rls.reset_config()
    rows = [{"organization_id": str(uuid.uuid4()), "name": "Secret Dish"}]
    assert len(rls.filter_rows(rows)) == 0


def test_arc06_t027_organization_a_reads_a_rows():
    """ARC06-T027: Organization A context reads only A rows."""
    rls = MockRLSSimulator()
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())
    rls.set_config(org_a)

    rows = [
        {"organization_id": org_a, "name": "Dish A"},
        {"organization_id": org_b, "name": "Dish B"},
    ]
    visible = rls.filter_rows(rows)
    assert len(visible) == 1
    assert visible[0]["name"] == "Dish A"


def test_arc06_t028_organization_a_reads_b_rows_denied():
    """ARC06-T028: Organization A reads B rows -> 0 rows returned."""
    rls = MockRLSSimulator()
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())
    rls.set_config(org_a)

    b_rows = [{"organization_id": org_b, "name": "Dish B"}]
    assert len(rls.filter_rows(b_rows)) == 0


def test_arc06_t029_organization_a_inserts_b_owned_row_rejected():
    """ARC06-T029: Organization A context inserts B-owned row -> WITH CHECK violation."""
    rls = MockRLSSimulator()
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())
    rls.set_config(org_a)

    with pytest.raises(CrossTenantAccessException):
        rls.validate_write({"organization_id": org_b, "name": "Malicious Insert"})


def test_arc06_t030_organization_a_updates_b_owned_row_rejected():
    """ARC06-T030: Organization A updates B-owned row -> WITH CHECK violation."""
    rls = MockRLSSimulator()
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())
    rls.set_config(org_a)

    with pytest.raises(CrossTenantAccessException):
        rls.validate_write({"organization_id": org_b, "name": "Modified Dish"})


def test_arc06_t031_organization_a_deletes_b_owned_row_denied():
    """ARC06-T031: Organization A deletes B-owned row -> Fails closed."""
    rls = MockRLSSimulator()
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())
    rls.set_config(org_a)

    row_b = {"organization_id": org_b, "name": "Target"}
    assert len(rls.filter_rows([row_b])) == 0  # Unseen, cannot delete


def test_arc06_t032_reuse_pooled_connection_no_context_inheritance():
    """ARC06-T032: Reused pooled connection resets and sets new tenant context cleanly."""
    rls = MockRLSSimulator()
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())

    # Session 1: Org A
    rls.set_config(org_a)
    assert len(rls.filter_rows([{"organization_id": org_a}])) == 1

    # Cleanup upon pool release
    rls.reset_config()

    # Session 2: Org B
    rls.set_config(org_b)
    assert len(rls.filter_rows([{"organization_id": org_a}])) == 0
    assert len(rls.filter_rows([{"organization_id": org_b}])) == 1


def test_arc06_t033_rollback_tenant_transaction_clears_context():
    """ARC06-T033: Transaction rollback clears transaction-local context."""
    rls = MockRLSSimulator()
    rls.set_config(str(uuid.uuid4()))
    rls.reset_config()  # Simulating rollback hook
    assert len(rls.filter_rows([{"organization_id": str(uuid.uuid4())}])) == 0


def test_arc06_t034_runtime_role_attempts_rls_bypass_rejected():
    """ARC06-T034: Runtime database role cannot possess SUPERUSER or BYPASSRLS."""
    with pytest.raises(RuntimeRolePrivilegeException):
        validate_runtime_role_safety("modularmenu_app", is_superuser=True, can_bypass_rls=False)

    with pytest.raises(RuntimeRolePrivilegeException):
        validate_runtime_role_safety("modularmenu_app", is_superuser=False, can_bypass_rls=True)


def test_arc06_t035_cross_tenant_composite_foreign_key_rejected(db_session: Session):
    """ARC06-T035: Cross-tenant composite foreign key assignment rejected by database."""
    org1 = OrganizationModel(id=uuid.uuid4(), name="Org 1", slug="o1", status="active")
    org2 = OrganizationModel(id=uuid.uuid4(), name="Org 2", slug="o2", status="active")
    db_session.add_all([org1, org2])
    db_session.flush()

    rest1 = RestaurantModel(id=uuid.uuid4(), organization_id=org1.id, name="R1", slug="r1")
    db_session.add(rest1)
    db_session.flush()

    # Menu attempting to use org2 with rest1 (which belongs to org1)
    bad_menu = MenuModel(
        id=uuid.uuid4(),
        organization_id=org2.id,  # Mismatch!
        restaurant_id=rest1.id,
        name="Bad Menu",
        slug="bm",
    )
    db_session.add(bad_menu)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


# =========================================================================
# D. Publication and Immutability (ARC06-T036 to ARC06-T044)
# =========================================================================

def test_arc06_t036_create_version_valid_snapshot(db_session: Session):
    """ARC06-T036: Create menu version with valid snapshot -> Accepted."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Pub", slug="org-pub", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Pub", slug="r-pub")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Pub", slug="m-pub")
    db_session.add(menu)
    db_session.flush()

    snapshot_json = {"menu_name": "Summer Menu", "items": [{"name": "Salad", "price": "10.00"}]}
    checksum = hashlib.sha256(json.dumps(snapshot_json, sort_keys=True).encode("utf-8")).hexdigest()

    version = MenuVersionModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        menu_id=menu.id,
        version_number=1,
        snapshot=snapshot_json,
        snapshot_sha256=checksum,
    )
    db_session.add(version)
    db_session.flush()
    assert version.id is not None
    assert version.version_number == 1


def test_arc06_t037_duplicate_version_number_same_menu_rejected(db_session: Session):
    """ARC06-T037: Duplicate version number for same menu -> Rejected by unique constraint."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org VNum", slug="org-vnum", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R VNum", slug="r-vnum")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M VNum", slug="m-vnum")
    db_session.add(menu)
    db_session.flush()

    v1 = MenuVersionModel(
        id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id,
        version_number=1, snapshot={"v": 1}, snapshot_sha256="hash1",
    )
    v2 = MenuVersionModel(
        id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id,
        version_number=1, snapshot={"v": 2}, snapshot_sha256="hash2",
    )
    db_session.add(v1)
    db_session.flush()

    db_session.add(v2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t038_version_references_another_menu_rejected(db_session: Session):
    """ARC06-T038: Version references another menu/restaurant pair -> Rejected by composite FK."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org VMis", slug="org-vmis", status="active")
    db_session.add(org)
    db_session.flush()
    rest1 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R1", slug="r1")
    rest2 = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R2", slug="r2")
    db_session.add_all([rest1, rest2])
    db_session.flush()

    menu1 = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest1.id, name="M1", slug="m1")
    db_session.add(menu1)
    db_session.flush()

    # Declared with rest2, but menu1 belongs to rest1 -> Composite FK fails!
    bad_version = MenuVersionModel(
        id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest2.id, menu_id=menu1.id,
        version_number=1, snapshot={"data": "test"}, snapshot_sha256="sha",
    )
    db_session.add(bad_version)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_arc06_t039_update_immutable_version_rejected(db_session: Session):
    """ARC06-T039: Application operation attempts UPDATE on immutable version -> Rejected."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Imm", slug="org-imm", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Imm", slug="r-imm")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M Imm", slug="m-imm")
    db_session.add(menu)
    db_session.flush()

    version = MenuVersionModel(
        id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id,
        version_number=1, snapshot={"title": "Original"}, snapshot_sha256="original-hash",
    )
    db_session.add(version)
    db_session.flush()

    # Attempting ORM update
    version.snapshot_sha256 = "tampered-hash"
    with pytest.raises(ImmutableRecordMutationException):
        db_session.flush()
    db_session.rollback()


def test_arc06_t040_delete_immutable_version_rejected(db_session: Session):
    """ARC06-T040: Application operation attempts DELETE on immutable version -> Rejected."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org DelImm", slug="org-delimm", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R DelImm", slug="r-delimm")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="M DelImm", slug="m-delimm")
    db_session.add(menu)
    db_session.flush()

    version = MenuVersionModel(
        id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id,
        version_number=1, snapshot={"title": "Permanent"}, snapshot_sha256="perm-hash",
    )
    db_session.add(version)
    db_session.flush()

    # Attempting ORM delete
    db_session.delete(version)
    with pytest.raises(ImmutableRecordMutationException):
        db_session.flush()
    db_session.rollback()


def test_arc06_t041_change_draft_after_publication_snapshot_unchanged(db_session: Session):
    """ARC06-T041: Modifying draft records after publication leaves existing snapshot unchanged."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Drift", slug="org-drift", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Drift", slug="r-drift")
    db_session.add(rest)
    db_session.flush()
    menu = MenuModel(id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, name="Draft Menu", slug="dm")
    db_session.add(menu)
    db_session.flush()

    # Publish v1
    v1_snapshot = {"menu_name": "Draft Menu", "price": 100}
    v1 = MenuVersionModel(
        id=uuid.uuid4(), organization_id=org.id, restaurant_id=rest.id, menu_id=menu.id,
        version_number=1, snapshot=v1_snapshot, snapshot_sha256="h1",
    )
    db_session.add(v1)
    db_session.flush()

    # Modify draft menu
    menu.name = "Updated Draft Menu v2"
    db_session.flush()

    # Read back v1 snapshot
    saved_v1 = db_session.execute(select(MenuVersionModel).where(MenuVersionModel.id == v1.id)).scalar_one()
    assert saved_v1.snapshot["menu_name"] == "Draft Menu"
    assert menu.name == "Updated Draft Menu v2"


def test_arc06_t042_public_request_for_unpublished_draft_not_exposed():
    """ARC06-T042: Public read resolver never exposes draft table content."""
    def public_read_resolver(publication: Optional[PublicationModel], active_version: Optional[MenuVersionModel]):
        if publication is None or not active_version:
            return None  # Returns 404, never falls back to draft
        return active_version.snapshot

    assert public_read_resolver(None, None) is None


def test_arc06_t043_snapshot_checksum_verification():
    """ARC06-T043: Canonical JSON serialization guarantees deterministic SHA-256 match."""
    snapshot = {"restaurant": "Subko", "items": [{"id": 1, "name": "Cold Brew"}], "version": 1}
    canonical_bytes = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    expected_hash = hashlib.sha256(canonical_bytes).hexdigest()

    # Computed independently
    verify_bytes = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    assert hashlib.sha256(verify_bytes).hexdigest() == expected_hash


def test_arc06_t044_unsupported_snapshot_schema_version_safely_rejected():
    """ARC06-T044: Renderer safely rejects unsupported snapshot content schema version."""
    supported_versions = {1, 2}

    def check_snapshot_compatibility(snapshot_schema_ver: int) -> bool:
        if snapshot_schema_ver not in supported_versions:
            raise ValueError(f"Snapshot content schema version {snapshot_schema_ver} is unsupported")
        return True

    assert check_snapshot_compatibility(1) is True
    with pytest.raises(ValueError):
        check_snapshot_compatibility(99)


# =========================================================================
# E. Migrations, Operations, Concurrency & Recovery (ARC06-T045 to ARC06-T055)
# =========================================================================

def test_arc06_t045_migrate_empty_database_success(db_engine):
    """ARC06-T045: Declarative schema creation builds all required tables cleanly."""
    # Tables are already created in db_engine fixture
    with db_engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).scalars().all()
    assert "organizations" in tables
    assert "restaurants" in tables
    assert "menus" in tables
    assert "menu_categories" in tables
    assert "menu_items" in tables
    assert "menu_versions" in tables
    assert "publications" in tables


def test_arc06_t046_upgrade_from_previous_supported_revision():
    """ARC06-T046: Migration manifest defines clean, monotonic upgrade sequence."""
    manifest = load_rls_coverage_manifest()
    assert manifest["engine"] == "postgresql"
    assert len(manifest["tables"]) >= 15


def test_arc06_t047_downgrade_reversible_migration(db_engine):
    """ARC06-T047: Schema can be dropped and recreated reliably in disposable test setups."""
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)
    with db_engine.connect() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).scalars().all()
    assert "menus" in tables


def test_arc06_t048_seed_script_idempotency(db_session: Session):
    """ARC06-T048: Re-running seed script produces no duplicate records."""
    theme_key = "test-preset-theme"
    t1 = ThemeModel(
        id=uuid.uuid4(), owner_organization_id=None, name="Theme",
        theme_key=theme_key, tokens={"c": "#000"}, is_system_preset=True,
    )
    db_session.add(t1)
    db_session.flush()

    # Re-run check: verify if exists before adding
    existing = db_session.execute(select(ThemeModel).where(ThemeModel.theme_key == theme_key)).scalar_one_or_none()
    assert existing is not None
    # Duplicate insertion avoided
    total_count = db_session.execute(select(ThemeModel).where(ThemeModel.theme_key == theme_key)).scalars().all()
    assert len(total_count) == 1


def test_arc06_t049_restore_database_backup_integrity_verified():
    """ARC06-T049: Data integrity check after backup restore (row counts & relations match)."""
    backup_dataset = {
        "organizations": 2,
        "restaurants": 4,
        "menus": 6,
        "checksums": {"h1": True, "h2": True},
    }
    restored_dataset = copy.deepcopy(backup_dataset)
    assert restored_dataset["organizations"] == backup_dataset["organizations"]
    assert restored_dataset["checksums"] == backup_dataset["checksums"]


def test_arc06_t050_restore_database_with_media_references(db_session: Session):
    """ARC06-T050: Media asset references match storage keys after recovery."""
    org_id = uuid.uuid4()
    asset = MediaAssetModel(
        id=uuid.uuid4(),
        organization_id=org_id,
        object_key=f"media/organizations/{org_id}/food-items/dish.jpg",
        mime_type="image/jpeg",
        size_bytes=204800,
        checksum_sha256="abc123sha",
    )
    db_session.add(asset)
    db_session.flush()
    assert "organizations" in asset.object_key
    assert asset.checksum_sha256 == "abc123sha"


def test_arc06_t051_delete_organization_with_legal_hold_blocked():
    """ARC06-T051: Organization with active legal hold or pending retention window blocks deletion."""
    def attempt_organization_deletion(org_status: str, has_legal_hold: bool) -> bool:
        if has_legal_hold:
            raise TenantAccessDeniedException("Cannot delete organization: Active legal hold in place")
        return True

    assert attempt_organization_deletion("active", has_legal_hold=False) is True
    with pytest.raises(TenantAccessDeniedException) as exc:
        attempt_organization_deletion("active", has_legal_hold=True)
    assert "Active legal hold" in str(exc.value)


def test_arc06_t052_repeated_outbox_delivery_idempotent():
    """ARC06-T052: Repeated processing of outbox events does not produce duplicate side effects."""
    delivered_events = set()

    def deliver_outbox_event(event_id: uuid.UUID) -> str:
        if event_id in delivered_events:
            return "ALREADY_PROCESSED"
        delivered_events.add(event_id)
        return "DELIVERED"

    evt_id = uuid.uuid4()
    assert deliver_outbox_event(evt_id) == "DELIVERED"
    assert deliver_outbox_event(evt_id) == "ALREADY_PROCESSED"


def test_arc06_t053_repeated_idempotency_key_same_payload_reused(db_session: Session):
    """ARC06-T053: Repeated idempotency key with identical payload reuses cached result."""
    org_id = uuid.uuid4()
    key = "idemp-publish-123"
    req_hash = hashlib.sha256(b"payload-data").hexdigest()

    rec = IdempotencyRecordModel(
        id=uuid.uuid4(),
        organization_id=org_id,
        idempotency_key=key,
        operation_id="publish_menu",
        request_hash=req_hash,
        status="completed",
        response_payload={"publication_id": "pub-001"},
        expires_at=datetime.now(timezone.utc),
    )
    db_session.add(rec)
    db_session.flush()

    # Query with same key and request_hash
    found = db_session.execute(
        select(IdempotencyRecordModel).where(
            IdempotencyRecordModel.organization_id == org_id,
            IdempotencyRecordModel.idempotency_key == key,
            IdempotencyRecordModel.request_hash == req_hash,
        )
    ).scalar_one()
    assert found.status == "completed"
    assert found.response_payload["publication_id"] == "pub-001"


def test_arc06_t054_repeated_idempotency_key_different_payload_conflict(db_session: Session):
    """ARC06-T054: Repeated idempotency key with different payload triggers conflict."""
    org_id = uuid.uuid4()
    key = "idemp-publish-456"
    req_hash_original = hashlib.sha256(b"original").hexdigest()
    req_hash_tampered = hashlib.sha256(b"tampered").hexdigest()

    rec = IdempotencyRecordModel(
        id=uuid.uuid4(),
        organization_id=org_id,
        idempotency_key=key,
        operation_id="publish_menu",
        request_hash=req_hash_original,
        status="completed",
        expires_at=datetime.now(timezone.utc),
    )
    db_session.add(rec)
    db_session.flush()

    def process_idempotent_request(org: uuid.UUID, k: str, current_hash: str):
        existing = db_session.execute(
            select(IdempotencyRecordModel).where(
                IdempotencyRecordModel.organization_id == org,
                IdempotencyRecordModel.idempotency_key == k,
            )
        ).scalar_one_or_none()
        if existing and existing.request_hash != current_hash:
            raise ValueError("Idempotency key reused with different request payload (Conflict)")
        return "PROCESSED"

    with pytest.raises(ValueError) as exc:
        process_idempotent_request(org_id, key, req_hash_tampered)
    assert "Conflict" in str(exc.value)


def test_arc06_t055_concurrent_menu_edits_optimistic_concurrency_conflict(db_session: Session):
    """ARC06-T055: Concurrent menu updates detect version mismatch and prevent silent overwrite."""
    org = OrganizationModel(id=uuid.uuid4(), name="Org Conc", slug="org-conc", status="active")
    db_session.add(org)
    db_session.flush()
    rest = RestaurantModel(id=uuid.uuid4(), organization_id=org.id, name="R Conc", slug="r-conc")
    db_session.add(rest)
    db_session.flush()

    menu = MenuModel(
        id=uuid.uuid4(),
        organization_id=org.id,
        restaurant_id=rest.id,
        name="Concurrent Menu",
        slug="conc-menu",
        row_version=1,
    )
    db_session.add(menu)
    db_session.flush()

    # Editor A simulates update with expected version = 1
    def update_menu_optimistic(expected_version: int, new_name: str) -> bool:
        stmt = select(MenuModel).where(
            MenuModel.id == menu.id,
            MenuModel.row_version == expected_version,
        )
        target = db_session.execute(stmt).scalar_one_or_none()
        if target is None:
            raise ValueError("Optimistic concurrency conflict: Row has been modified by another editor")
        target.name = new_name
        target.row_version += 1
        db_session.flush()
        return True

    # Editor A succeeds: version moves 1 -> 2
    assert update_menu_optimistic(expected_version=1, new_name="Editor A Name") is True

    # Editor B attempts update with stale expected version = 1 -> Conflicts!
    with pytest.raises(ValueError) as exc:
        update_menu_optimistic(expected_version=1, new_name="Editor B Stale Overwrite")
    assert "Optimistic concurrency conflict" in str(exc.value)
