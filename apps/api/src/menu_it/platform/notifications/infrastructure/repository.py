"""Notification persistence repository (FCD-09 WP-03)."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.notification import NotificationDeliveryModel, NotificationModel


class NotificationRepository:
    """Handles in-app notification queries and delivery tracking persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_in_app(
        self,
        *,
        notification_id: UUID,
        organization_id: UUID | None,
        recipient_user_id: UUID,
        type: str,
        title: str,
        body: str,
        payload: dict[str, Any] | None = None,
    ) -> NotificationModel:
        model = NotificationModel(
            id=notification_id,
            organization_id=organization_id,
            recipient_user_id=recipient_user_id,
            type=type,
            title=title,
            body=body,
            payload=payload,
            created_at=datetime.now(UTC),
        )
        self.session.add(model)
        await self.session.flush()
        return model

    async def list_in_app_for_user(
        self,
        recipient_user_id: UUID,
        *,
        organization_id: UUID | None = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NotificationModel]:
        stmt = select(NotificationModel).where(
            NotificationModel.recipient_user_id == recipient_user_id
        )
        if organization_id is not None:
            stmt = stmt.where(
                (NotificationModel.organization_id == organization_id)
                | (NotificationModel.organization_id.is_(None))
            )
        if unread_only:
            stmt = stmt.where(NotificationModel.read_at.is_(None))

        stmt = stmt.order_by(NotificationModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: UUID, recipient_user_id: UUID) -> bool:
        stmt = (
            update(NotificationModel)
            .where(
                NotificationModel.id == notification_id,
                NotificationModel.recipient_user_id == recipient_user_id,
                NotificationModel.read_at.is_(None),
            )
            .values(read_at=datetime.now(UTC))
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def record_delivery(
        self,
        *,
        delivery_id: UUID,
        notification_id: UUID,
        channel: str,
        status: str,
        provider_reference: str | None,
        idempotency_key: str,
        error_code: str | None = None,
    ) -> NotificationDeliveryModel:
        delivery = NotificationDeliveryModel(
            id=delivery_id,
            notification_id=notification_id,
            channel=channel,
            status=status,
            provider_reference=provider_reference,
            idempotency_key=idempotency_key,
            error_code=error_code,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.session.add(delivery)
        await self.session.flush()
        return delivery

    async def get_delivery_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> NotificationDeliveryModel | None:
        stmt = select(NotificationDeliveryModel).where(
            NotificationDeliveryModel.idempotency_key == idempotency_key
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
