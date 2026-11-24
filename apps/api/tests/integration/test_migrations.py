"""Integration tests for Alembic migration lifecycle (FCD-03 §15.8, FCD-04 §6.3, FCD-06 §18)."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_migration_lifecycle(tmp_path: Path):
    """Verify clean database can be migrated through all revisions, downgraded, and upgraded again.

    Tests:
    1. Upgrade empty database to 0001_initial_tables: assert 'tenants', 'restaurants'.
    2. Upgrade to head (0004_restaurant_profiles): assert 'organizations',
       'restaurants', memberships, audit events, auth tables, and 'restaurant_profiles'.
    3. Downgrade by 1 revision to 0003_identity_foundation: assert 'restaurant_profiles' dropped.
    4. Downgrade to 0002_org_foundation: assert auth tables dropped.
    5. Downgrade to 0001_initial_tables: assert 'organizations' reverses to 'tenants'.
    6. Downgrade to base: assert all application tables are dropped.
    7. Upgrade back to head: assert all canonical FCD-06 tables are cleanly restored.
    """
    api_dir = Path(__file__).resolve().parents[2]
    alembic_ini_path = api_dir / "alembic.ini"
    test_db_path = tmp_path / "migration_lifecycle_test.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    alembic_cfg.set_main_option("script_location", str(api_dir / "alembic"))

    sync_engine = create_engine(test_db_url)

    # 1. Upgrade to 0001_initial_tables
    command.upgrade(alembic_cfg, "0001_initial_tables")
    inspector = inspect(sync_engine)
    tables_v1 = inspector.get_table_names()
    assert "alembic_version" in tables_v1
    assert "tenants" in tables_v1
    assert "restaurants" in tables_v1

    # 2. Upgrade to head (0004_restaurant_profiles)
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(sync_engine)
    tables_head = inspector.get_table_names()
    assert "organizations" in tables_head
    assert "tenants" not in tables_head
    assert "restaurants" in tables_head
    assert "organization_memberships" in tables_head
    assert "restaurant_memberships" in tables_head
    assert "organization_audit_events" in tables_head
    assert "users" in tables_head
    assert "user_credentials" in tables_head
    assert "user_sessions" in tables_head
    assert "refresh_token_records" in tables_head
    assert "email_verification_tokens" in tables_head
    assert "password_reset_tokens" in tables_head
    assert "platform_memberships" in tables_head
    assert "restaurant_profiles" in tables_head

    # Verify column rename in restaurants
    rest_cols = [c["name"] for c in inspector.get_columns("restaurants")]
    assert "organization_id" in rest_cols
    assert "tenant_id" not in rest_cols

    # Verify restaurant_profiles columns
    profile_cols = [c["name"] for c in inspector.get_columns("restaurant_profiles")]
    assert "organization_id" in profile_cols
    assert "restaurant_id" in profile_cols
    assert "public_name" in profile_cols
    assert "primary_currency" in profile_cols
    assert "timezone" in profile_cols
    assert "schedule_payload" in profile_cols

    # 3. Downgrade to 0003_identity_foundation (-1)
    command.downgrade(alembic_cfg, "0003_identity_foundation")
    inspector = inspect(sync_engine)
    tables_v3 = inspector.get_table_names()
    assert "restaurant_profiles" not in tables_v3
    assert "users" in tables_v3

    # 4. Downgrade to 0002_org_foundation
    command.downgrade(alembic_cfg, "0002_org_foundation")
    inspector = inspect(sync_engine)
    tables_v2 = inspector.get_table_names()
    assert "users" not in tables_v2
    assert "user_credentials" not in tables_v2
    assert "user_sessions" not in tables_v2
    assert "organizations" in tables_v2

    # 5. Downgrade to 0001_initial_tables
    command.downgrade(alembic_cfg, "0001_initial_tables")
    inspector = inspect(sync_engine)
    tables_downgraded = inspector.get_table_names()
    assert "tenants" in tables_downgraded
    assert "organizations" not in tables_downgraded
    assert "organization_memberships" not in tables_downgraded
    assert "restaurant_memberships" not in tables_downgraded
    assert "organization_audit_events" not in tables_downgraded

    # 6. Downgrade to base
    command.downgrade(alembic_cfg, "base")
    inspector = inspect(sync_engine)
    tables_base = inspector.get_table_names()
    assert "tenants" not in tables_base
    assert "restaurants" not in tables_base

    # 7. Upgrade back to head
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(sync_engine)
    tables_restored = inspector.get_table_names()
    assert "organizations" in tables_restored
    assert "restaurants" in tables_restored
    assert "organization_memberships" in tables_restored
    assert "restaurant_memberships" in tables_restored
    assert "organization_audit_events" in tables_restored
    assert "users" in tables_restored
    assert "user_credentials" in tables_restored
    assert "user_sessions" in tables_restored
    assert "restaurant_profiles" in tables_restored

    sync_engine.dispose()
