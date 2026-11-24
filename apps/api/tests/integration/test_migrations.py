"""Integration tests for Alembic migration lifecycle (FCD-03 §15.8)."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_migration_lifecycle(tmp_path: Path):
    """Verify clean database can be migrated to head, inspected, downgraded, and upgraded again.

    Tests:
    1. Upgrade empty database to head.
    2. Inspect schema: assert 'tenants', 'restaurants', and 'alembic_version' exist.
    3. Downgrade by 1 revision to base: assert application tables are dropped.
    4. Upgrade back to head: assert application tables are cleanly restored.
    """
    api_dir = Path(__file__).resolve().parents[2]
    alembic_ini_path = api_dir / "alembic.ini"
    test_db_path = tmp_path / "migration_lifecycle_test.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    alembic_cfg.set_main_option("script_location", str(api_dir / "alembic"))

    # 1. Upgrade from empty database to head
    command.upgrade(alembic_cfg, "head")

    sync_engine = create_engine(test_db_url)
    inspector = inspect(sync_engine)
    tables = inspector.get_table_names()

    assert "alembic_version" in tables
    assert "tenants" in tables
    assert "restaurants" in tables

    # Verify column structures
    tenant_cols = [c["name"] for c in inspector.get_columns("tenants")]
    assert "id" in tenant_cols
    assert "name" in tenant_cols
    assert "slug" in tenant_cols
    assert "status" in tenant_cols
    assert "created_at" in tenant_cols
    assert "updated_at" in tenant_cols

    restaurant_cols = [c["name"] for c in inspector.get_columns("restaurants")]
    assert "id" in restaurant_cols
    assert "tenant_id" in restaurant_cols
    assert "slug" in restaurant_cols
    assert "timezone" in restaurant_cols

    # 2. Downgrade to base (-1)
    command.downgrade(alembic_cfg, "-1")
    inspector = inspect(sync_engine)
    downgraded_tables = inspector.get_table_names()
    assert "tenants" not in downgraded_tables
    assert "restaurants" not in downgraded_tables

    # 3. Upgrade back to head
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(sync_engine)
    reupgraded_tables = inspector.get_table_names()
    assert "tenants" in reupgraded_tables
    assert "restaurants" in reupgraded_tables

    sync_engine.dispose()
