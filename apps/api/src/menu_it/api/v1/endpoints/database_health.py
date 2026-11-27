"""Database health check endpoint (FCD-03 §11.3)."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from menu_it.database.session import AsyncSessionFactory

router = APIRouter(
    prefix="/database",
    tags=["Database"],
)


@router.get("/health")
async def database_health():
    """Verify database connectivity via lightweight SELECT 1 check.

    Returns sanitized status without leaking connection details or credentials.
    """
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "reachable",
        }
    except (SQLAlchemyError, OSError, Exception) as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unavailable",
                "database": "unreachable",
            },
        ) from exc
