"""Integration tests for Alembic migration lifecycle (FCD-03 §15.8, FCD-04 §6.3, §18)."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_migration_lifecycle(tmp_path: Path):
    """Verify clean database can be migrated through all revisions, downgraded, and upgraded again.

    Tests:
    1. Upgrade empty database to 0001_initial_tables: assert 'tenants', 'restaurants'.
    2. Upgrade to head (0002_org_foundation): assert 'organizations',
       'restaurants' (organization_id), memberships, and audit events.
    3. Downgrade by 1 revision to 0001: assert 'organizations' reverses to 'tenants'.
    4. Downgrade to base: assert all application tables are dropped.
    5. Upgrade back to head: assert all canonical FCD-04 tables are cleanly restored.
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

    # 2. Upgrade to head (0002_org_foundation)
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(sync_engine)
    tables_v2 = inspector.get_table_names()
    assert "organizations" in tables_v2
    assert "tenants" not in tables_v2
    assert "restaurants" in tables_v2
    assert "organization_memberships" in tables_v2
    assert "restaurant_memberships" in tables_v2
    assert "organization_audit_events" in tables_v2

    # Verify column rename in restaurants
    rest_cols = [c["name"] for c in inspector.get_columns("restaurants")]
    assert "organization_id" in rest_cols
    assert "tenant_id" not in rest_cols

    # 3. Downgrade to 0001_initial_tables (-1)
    command.downgrade(alembic_cfg, "-1")
    inspector = inspect(sync_engine)
    tables_downgraded = inspector.get_table_names()
    assert "tenants" in tables_downgraded
    assert "organizations" not in tables_downgraded
    assert "organization_memberships" not in tables_downgraded
    assert "restaurant_memberships" not in tables_downgraded
    assert "organization_audit_events" not in tables_downgraded

    # 4. Downgrade to base
    command.downgrade(alembic_cfg, "base")
    inspector = inspect(sync_engine)
    tables_base = inspector.get_table_names()
    assert "tenants" not in tables_base
    assert "restaurants" not in tables_base

    # 5. Upgrade back to head
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(sync_engine)
    tables_restored = inspector.get_table_names()
    assert "organizations" in tables_restored
    assert "restaurants" in tables_restored
    assert "organization_memberships" in tables_restored
    assert "restaurant_memberships" in tables_restored
    assert "organization_audit_events" in tables_restored

    sync_engine.dispose()
