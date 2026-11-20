"""
ModularMenu — Database Runtime Role & Privilege Enforcement (ARC-05 §8.4, ARC05-D10).
Guarantees runtime database user lacks BYPASSRLS and SUPERUSER privileges.
"""
from app.shared.domain.tenant_exceptions import TenantSecurityException


class RuntimeRolePrivilegeException(TenantSecurityException):
    """Raised when the database runtime role has prohibited superuser or bypassrls privileges."""
    pass


def generate_runtime_role_ddl(role_name: str = "modularmenu_app") -> str:
    """
    Generates DDL for creating the least-privilege application runtime role.
    Explicitly forbids SUPERUSER, BYPASSRLS, CREATEDB, and CREATEROLE.
    """
    return f"""-- Least-privilege application database role (ARC-05 §8.4)
CREATE ROLE {role_name} WITH
    LOGIN
    NOSUPERUSER
    NOBYPASSRLS
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;

-- Grant execution permissions
GRANT USAGE ON SCHEMA public TO {role_name};
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {role_name};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role_name};
"""


def validate_runtime_role_safety(
    role_name: str,
    is_superuser: bool,
    can_bypass_rls: bool,
) -> bool:
    """
    Validates that a database connection role does not have bypass capabilities.
    Fails closed if the runtime role is superuser or has bypassrls enabled.
    """
    if is_superuser:
        raise RuntimeRolePrivilegeException(
            f"Security Violation (ARC05-D10): Runtime database role '{role_name}' has SUPERUSER privileges!"
        )
    if can_bypass_rls:
        raise RuntimeRolePrivilegeException(
            f"Security Violation (ARC05-D10): Runtime database role '{role_name}' has BYPASSRLS privileges!"
        )
    return True
