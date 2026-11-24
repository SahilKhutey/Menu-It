"""Tenant-aware transaction management and Unit of Work (FCD-04 §12.4, §13.2)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.tenant_scope import set_database_tenant_context
from menu_it.tenancy.context import TenantContext


@asynccontextmanager
async def tenant_transaction(
    session: AsyncSession,
    context: TenantContext,
) -> AsyncIterator[AsyncSession]:
    """Context manager opening an atomic transaction bound to an immutable TenantContext.

    Sets transaction-local organization ID, executes operations, commits on success,
    and automatically rolls back on exception.
    """
    async with session.begin():
        await set_database_tenant_context(session, context)
        yield session


class TenantUnitOfWork:
    """Reusable Unit of Work binding an AsyncSession with an immutable TenantContext."""

    def __init__(self, session: AsyncSession, context: TenantContext):
        self.session = session
        self.context = context
        self._transaction = None

    async def __aenter__(self) -> "TenantUnitOfWork":
        self._transaction = self.session.begin()
        await self._transaction.__aenter__()
        try:
            await set_database_tenant_context(self.session, self.context)
        except Exception:
            await self._transaction.__aexit__(None, None, None)
            raise
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        if self._transaction:
            return await self._transaction.__aexit__(exc_type, exc_val, exc_tb)
        return None
