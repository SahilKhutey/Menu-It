"""
ModularMenu — PostgreSQL Transaction-Local Tenant Session Management (ARC-05 §8.2, ARC05-D11).
Enforces transaction-scoped tenant identity via 'app.current_organization_id'
and guarantees clean teardown across connection pooling.
"""
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.shared.domain.tenant_exceptions import InvalidTenantContextException

TENANT_CONFIG_KEY = "app.current_organization_id"


def set_tenant_transaction_context_sync(session: Session, organization_id: Optional[UUID]) -> None:
    """
    Sets the PostgreSQL session config for the duration of the current transaction.
    Passing is_local=true guarantees context is discarded upon COMMIT or ROLLBACK.
    """
    if organization_id is None:
        # Reset context to empty to fail closed
        session.execute(text(f"SELECT set_config('{TENANT_CONFIG_KEY}', '', true)"))
    else:
        session.execute(
            text(f"SELECT set_config('{TENANT_CONFIG_KEY}', :org_id, true)"),
            {"org_id": str(organization_id)},
        )


async def set_tenant_transaction_context_async(
    session: AsyncSession, organization_id: Optional[UUID]
) -> None:
    """
    Async variant for asyncpg / SQLAlchemy AsyncSession.
    """
    if organization_id is None:
        await session.execute(text(f"SELECT set_config('{TENANT_CONFIG_KEY}', '', true)"))
    else:
        await session.execute(
            text(f"SELECT set_config('{TENANT_CONFIG_KEY}', :org_id, true)"),
            {"org_id": str(organization_id)},
        )


def reset_tenant_context_sync(session: Session) -> None:
    """Explicitly clears the tenant setting before returning connection to pool."""
    session.execute(text(f"SELECT set_config('{TENANT_CONFIG_KEY}', '', true)"))


async def reset_tenant_context_async(session: AsyncSession) -> None:
    """Explicitly clears the tenant setting in async session."""
    await session.execute(text(f"SELECT set_config('{TENANT_CONFIG_KEY}', '', true)"))


@contextmanager
def tenant_transaction_scope_sync(
    session: Session, organization_id: UUID
) -> Generator[Session, None, None]:
    """
    Context manager guaranteeing transaction-local context and post-execution cleanup.
    """
    if not organization_id:
        raise InvalidTenantContextException("Cannot establish tenant scope with empty organization_id")
    try:
        set_tenant_transaction_context_sync(session, organization_id)
        yield session
    finally:
        reset_tenant_context_sync(session)


@asynccontextmanager
async def tenant_transaction_scope_async(
    session: AsyncSession, organization_id: UUID
) -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager guaranteeing transaction-local context and post-execution cleanup.
    """
    if not organization_id:
        raise InvalidTenantContextException("Cannot establish tenant scope with empty organization_id")
    try:
        await set_tenant_transaction_context_async(session, organization_id)
        yield session
    finally:
        await reset_tenant_context_async(session)
