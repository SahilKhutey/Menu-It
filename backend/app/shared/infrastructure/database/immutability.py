"""
ModularMenu — Database Immutability Protections (ARC-06 §6.4, ARC06-D16).
Rejects UPDATE and DELETE operations on immutable records (MenuVersion, AuditLog, OutboxEvent).
"""
from typing import Type
from sqlalchemy import event
from sqlalchemy.orm import Mapper, Session

from app.shared.domain.tenant_exceptions import TenantSecurityException


class ImmutableRecordMutationException(TenantSecurityException):
    """Raised when an application operation attempts to update or delete an immutable record."""
    def __init__(self, message: str = "Immutable records cannot be updated or deleted"):
        super().__init__(message)


def register_immutability_guard(model_cls: Type[object]) -> None:
    """
    Registers SQLAlchemy event listeners on the given model to strictly forbid
    ORM updates and deletions during normal application operations.
    """
    @event.listens_for(model_cls, "before_update")
    def receive_before_update(mapper: Mapper, connection, target):
        raise ImmutableRecordMutationException(
            f"Security Violation: Entity '{target.__class__.__name__}' (id={getattr(target, 'id', 'unknown')}) "
            f"is immutable and cannot be updated."
        )

    @event.listens_for(model_cls, "before_delete")
    def receive_before_delete(mapper: Mapper, connection, target):
        raise ImmutableRecordMutationException(
            f"Security Violation: Entity '{target.__class__.__name__}' (id={getattr(target, 'id', 'unknown')}) "
            f"is immutable and cannot be deleted through standard operations."
        )
