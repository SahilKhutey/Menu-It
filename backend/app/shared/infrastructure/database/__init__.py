"""
Shared database infrastructure package (declarative base, naming, session, unit of work, immutability).
"""

from app.shared.infrastructure.database.base import (
    POSTGRES_NAMING_CONVENTIONS,
    Base,
    ImmutableTimestamped,
    RestaurantScoped,
    TenantScoped,
    Timestamped,
    UUIDPrimaryKey,
)
from app.shared.infrastructure.database.immutability import (
    ImmutableRecordMutationException,
    register_immutability_guard,
)
from app.shared.infrastructure.database.session import (
    AsyncSessionFactory,
    engine,
    get_tenant_db_session,
)
from app.shared.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork

__all__ = [
    "Base",
    "UUIDPrimaryKey",
    "Timestamped",
    "ImmutableTimestamped",
    "TenantScoped",
    "RestaurantScoped",
    "POSTGRES_NAMING_CONVENTIONS",
    "ImmutableRecordMutationException",
    "register_immutability_guard",
    "engine",
    "AsyncSessionFactory",
    "get_tenant_db_session",
    "SqlAlchemyUnitOfWork",
]
