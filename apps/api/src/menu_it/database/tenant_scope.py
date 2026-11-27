"""Transaction-local database tenant context setting (FCD-04 §12.3)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.tenancy.context import TenantContext


async def set_database_tenant_context(
    session: AsyncSession,
    context: TenantContext,
) -> None:
    """Set transaction-local organization ID in PostgreSQL.

    Uses set_config(..., true) so the setting is strictly transaction-local
    and is automatically cleared upon commit or rollback, preventing context leakage
    across pooled database connections.
    """
    bind = session.bind
    if bind and "postgresql" in bind.dialect.name:
        await session.execute(
            text(
                """
                SELECT set_config(
                    'app.current_organization_id',
                    :organization_id,
                    true
                )
                """
            ),
            {"organization_id": str(context.organization_id)},
        )
