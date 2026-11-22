"""
ModularMenu — SQLAlchemy Unit of Work with Tenant Context Binding (ARC-06 §8.7, ARC06-D18).
Coordinates atomic database transactions and binds tenant context to the transaction.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.database.tenant_session import (
    reset_tenant_context_async,
    set_tenant_transaction_context_async,
)
from app.shared.application.tenant_context import TenantContext


class SqlAlchemyUnitOfWork:
    """
    Asynchronous Unit of Work coordinating business transaction boundaries.
    Automatically applies transaction-scoped PostgreSQL RLS tenant context
    and cleans up session state upon exit.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        tenant_context: TenantContext | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.tenant_context = tenant_context
        self.session: AsyncSession | None = None
        self.transaction = None
        self.committed: bool = False
        self.rolled_back: bool = False

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.transaction = await self.session.begin()

        # If tenant context is present, establish transaction-local config
        if self.tenant_context is not None and "sqlite" not in str(self.session.bind.url):
            await set_tenant_transaction_context_async(
                self.session, self.tenant_context.organization_id
            )

        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None:
                await self.transaction.commit()
                self.committed = True
            else:
                await self.transaction.rollback()
                self.rolled_back = True
        finally:
            if self.session is not None:
                if self.tenant_context is not None and "sqlite" not in str(self.session.bind.url):
                    await reset_tenant_context_async(self.session)
                await self.session.close()
