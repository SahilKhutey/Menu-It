"""
Infrastructure database adapters (RLS, roles, transaction-local tenant session).
"""

from app.infrastructure.database.rls import (
    MockRLSSimulator,
    generate_enable_rls_sql,
    generate_force_rls_sql,
    generate_full_table_rls_ddl,
    generate_policy_sql,
    load_rls_coverage_manifest,
)
from app.infrastructure.database.roles import (
    RuntimeRolePrivilegeException,
    generate_runtime_role_ddl,
    validate_runtime_role_safety,
)
from app.infrastructure.database.tenant_session import (
    TENANT_CONFIG_KEY,
    reset_tenant_context_async,
    reset_tenant_context_sync,
    set_tenant_transaction_context_async,
    set_tenant_transaction_context_sync,
    tenant_transaction_scope_async,
    tenant_transaction_scope_sync,
)

__all__ = [
    "generate_enable_rls_sql",
    "generate_force_rls_sql",
    "generate_policy_sql",
    "generate_full_table_rls_ddl",
    "load_rls_coverage_manifest",
    "MockRLSSimulator",
    "RuntimeRolePrivilegeException",
    "generate_runtime_role_ddl",
    "validate_runtime_role_safety",
    "TENANT_CONFIG_KEY",
    "set_tenant_transaction_context_sync",
    "set_tenant_transaction_context_async",
    "reset_tenant_context_sync",
    "reset_tenant_context_async",
    "tenant_transaction_scope_sync",
    "tenant_transaction_scope_async",
]
