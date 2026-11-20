"""
ModularMenu — Operations, Governance & Outbox Models (ARC-06 §3.2, §10.3, §10.4).
Audit trails, transactional outbox events, and idempotency records.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import GUID, PortableJSON
from app.shared.infrastructure.database.base import Base, UUIDPrimaryKey
from app.shared.infrastructure.database.immutability import register_immutability_guard


class AuditLogModel(Base, UUIDPrimaryKey):
    __tablename__ = "audit_logs"

    organization_id: Mapped[Optional[UUID]] = mapped_column(GUID(), nullable=True, index=True)
    actor_id: Mapped[Optional[UUID]] = mapped_column(GUID(), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[UUID]] = mapped_column(GUID(), nullable=True)
    outcome: Mapped[str] = mapped_column(String(30), default="SUCCESS", nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(PortableJSON(), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


register_immutability_guard(AuditLogModel)


class OutboxEventModel(Base, UUIDPrimaryKey):
    __tablename__ = "outbox_events"

    organization_id: Mapped[Optional[UUID]] = mapped_column(GUID(), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(GUID(), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(PortableJSON(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


register_immutability_guard(OutboxEventModel)


class IdempotencyRecordModel(Base, UUIDPrimaryKey):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("organization_id", "idempotency_key", name="uq_idempotency_org_key"),
    )

    organization_id: Mapped[UUID] = mapped_column(GUID(), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    operation_id: Mapped[str] = mapped_column(String(100), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="processing", nullable=False)
    response_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(PortableJSON(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
