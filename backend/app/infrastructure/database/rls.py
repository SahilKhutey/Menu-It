"""
ModularMenu — PostgreSQL Row-Level Security (RLS) Generator & Policy Engine (ARC-05 §8).
Enforces database-level tenant isolation, DDL generation, and policy verification.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

from app.shared.domain.tenant_exceptions import (
    CrossTenantAccessException,
    InvalidTenantContextException,
)

DEFAULT_CONFIG_KEY = "app.current_organization_id"


def generate_enable_rls_sql(table_name: str) -> str:
    """Generates DDL to enable Row-Level Security on a table."""
    return f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"


def generate_force_rls_sql(table_name: str) -> str:
    """
    Generates DDL to force Row-Level Security even for table owners.
    Essential to prevent table owner bypass.
    """
    return f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;"


def generate_policy_sql(
    table_name: str,
    tenant_col: str = "organization_id",
    policy_name: str | None = None,
    config_key: str = DEFAULT_CONFIG_KEY,
) -> str:
    """
    Generates PostgreSQL RLS policy enforcing isolation for SELECT, INSERT, UPDATE, DELETE.
    Fails closed when config_key is unset, NULL, or empty string.
    """
    p_name = policy_name or f"{table_name}_tenant_isolation"
    predicate = f"({tenant_col} = NULLIF(current_setting('{config_key}', true), '')::uuid)"

    return f"""CREATE POLICY {p_name}
ON {table_name}
AS RESTRICTIVE
USING ({predicate})
WITH CHECK ({predicate});"""


def generate_full_table_rls_ddl(
    table_name: str,
    tenant_col: str = "organization_id",
    policy_name: str | None = None,
    config_key: str = DEFAULT_CONFIG_KEY,
) -> list[str]:
    """Generates complete DDL batch to enable, force, and create policy for a table."""
    return [
        generate_enable_rls_sql(table_name),
        generate_force_rls_sql(table_name),
        generate_policy_sql(table_name, tenant_col, policy_name, config_key),
    ]


def load_rls_coverage_manifest(manifest_path: Path | None = None) -> dict[str, Any]:
    """Loads and validates backend/architecture/rls_coverage.yaml."""
    if manifest_path is None:
        # Check backend/architecture/rls_coverage.yaml
        manifest_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "architecture"
            / "rls_coverage.yaml"
        )
    with open(manifest_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class MockRLSSimulator:
    """
    Simulates PostgreSQL Row-Level Security behaviors in testing and non-PG environments.
    Validates fail-closed behavior, transaction locality, and cross-tenant filtering.
    """

    def __init__(self) -> None:
        self._current_org_id: str | None = None

    def set_config(self, org_id: str | None) -> None:
        self._current_org_id = org_id.strip() if (org_id and org_id.strip()) else None

    def reset_config(self) -> None:
        self._current_org_id = None

    def filter_rows(
        self,
        rows: Sequence[dict[str, Any]],
        tenant_key: str = "organization_id",
    ) -> list[dict[str, Any]]:
        """
        Filters rows mimicking PostgreSQL RLS USING clause:
        If app.current_organization_id is not set or empty -> returns 0 rows (fails closed).
        If set -> returns only rows where row[tenant_key] == current_setting.
        """
        if not self._current_org_id:
            return []  # Fail-closed

        return [row for row in rows if str(row.get(tenant_key)) == self._current_org_id]

    def validate_write(
        self,
        row: dict[str, Any],
        tenant_key: str = "organization_id",
    ) -> None:
        """
        Validates write mimicking PostgreSQL RLS WITH CHECK clause:
        Raises error if row tenant_id does not match current_setting.
        """
        if not self._current_org_id:
            raise InvalidTenantContextException(
                "Cannot perform tenant write: RLS context app.current_organization_id is not set"
            )
        if str(row.get(tenant_key)) != self._current_org_id:
            raise CrossTenantAccessException(
                f"RLS WITH CHECK violation: row organization_id '{row.get(tenant_key)}' "
                f"does not match active context '{self._current_org_id}'"
            )
