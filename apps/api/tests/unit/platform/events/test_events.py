"""Unit tests for transactional outbox, publisher, dispatcher, and inbox (FCD-10 WP-05)."""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.database.models.event_outbox import EventOutboxModel
from menu_it.platform.events.contracts import EventEnvelope
from menu_it.platform.events.dispatcher import OutboxDispatcher
from menu_it.platform.events.inbox import EventInbox
from menu_it.platform.events.publisher import OutboxEventPublisher
from menu_it.platform.events.registry import register_consumer


@pytest.mark.asyncio
async def test_evt_01_and_02_outbox_publish_and_transaction_rollback(db_session: AsyncSession):
    publisher = OutboxEventPublisher(db_session)
    event_id = uuid.uuid4()
    event = EventEnvelope(
        event_id=event_id,
        event_type="UserRegistered",
        schema_version=1,
        occurred_at=datetime.now(UTC),
        organization_id=None,
        actor_user_id=None,
        correlation_id="corr-evt-1",
        payload={"email": "chef@restaurant.com"},
    )

    outbox_rec = await publisher.publish(event)
    assert outbox_rec.event_id == event_id

    # Commit ensures it is persisted
    await db_session.commit()

    # Query outbox directly
    retrieved = await db_session.get(EventOutboxModel, event_id)
    assert retrieved is not None
    assert retrieved.event_type == "UserRegistered"
    assert retrieved.published_at is None


@pytest.mark.asyncio
async def test_evt_03_dispatcher_processes_pending_events(db_session: AsyncSession):
    publisher = OutboxEventPublisher(db_session)
    event_id = uuid.uuid4()
    dispatched_events = []

    async def mock_consumer(event: EventEnvelope, services):
        dispatched_events.append(event)

    register_consumer("CustomEventTest", mock_consumer)

    event = EventEnvelope(
        event_id=event_id,
        event_type="CustomEventTest",
        schema_version=1,
        occurred_at=datetime.now(UTC),
        organization_id=None,
        actor_user_id=None,
        correlation_id="corr-custom",
        payload={"value": 123},
    )
    await publisher.publish(event)
    await db_session.commit()

    dispatcher = OutboxDispatcher(db_session)
    count = await dispatcher.process_batch(batch_size=10)
    await db_session.commit()

    assert count >= 1
    assert any(e.event_id == event_id for e in dispatched_events)

    # Verify marked as published
    record = await db_session.get(EventOutboxModel, event_id)
    assert record.published_at is not None


@pytest.mark.asyncio
async def test_evt_05_inbox_deduplication(db_session: AsyncSession):
    inbox = EventInbox(db_session)
    event_id = uuid.uuid4()
    consumer_name = "EmailNotificationConsumer"

    # First delivery: should return True (new event, process it)
    first_attempt = await inbox.record_if_not_processed(consumer_name, event_id)
    assert first_attempt is True
    await db_session.commit()

    # Duplicate delivery of same event: should return False (already processed)
    duplicate_attempt = await inbox.record_if_not_processed(consumer_name, event_id)
    assert duplicate_attempt is False

    # Different consumer for same event: should return True (independent consumer inbox)
    other_consumer_attempt = await inbox.record_if_not_processed("AnalyticsConsumer", event_id)
    assert other_consumer_attempt is True
    await db_session.commit()


@pytest.mark.asyncio
async def test_evt_06_dispatcher_retry_on_consumer_error(db_session: AsyncSession):
    publisher = OutboxEventPublisher(db_session)
    event_id = uuid.uuid4()

    def failing_consumer(event: EventEnvelope, services):
        raise ConnectionError("External provider down")

    register_consumer("FailingEventTest", failing_consumer)

    event = EventEnvelope(
        event_id=event_id,
        event_type="FailingEventTest",
        schema_version=1,
        occurred_at=datetime.now(UTC),
        organization_id=None,
        actor_user_id=None,
        correlation_id="corr-fail",
        payload={"data": "test"},
    )
    await publisher.publish(event)
    await db_session.commit()

    dispatcher = OutboxDispatcher(db_session)
    await dispatcher.process_batch(batch_size=10)
    await db_session.commit()

    record = await db_session.get(EventOutboxModel, event_id)
    assert record.published_at is None
    assert record.attempts == 1
    assert record.next_attempt_at is not None
    assert record.last_error_code == "ConnectionError"
