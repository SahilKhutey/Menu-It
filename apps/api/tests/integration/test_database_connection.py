"""Integration tests for database connectivity (FCD-03 §15.9)."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Verify database engine executes basic query and returns expected scalar."""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar_one() == 1
