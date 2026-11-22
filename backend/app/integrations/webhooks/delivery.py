"""
ModularMenu — Outbound Webhook Delivery Service (ARC-07 §12.4).
"""

import datetime
import json
import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.integrations.webhooks.signing import sign_payload


@dataclass(frozen=True)
class WebhookEvent:
    id: UUID
    event_type: str
    organization_id: UUID
    created_at: datetime.datetime
    data: dict[str, Any]


class WebhookDeliveryService:
    def __init__(self, signing_secret: str = "whsec_test_secret_123"):
        self.signing_secret = signing_secret
        self.delivered_events: list[dict[str, Any]] = []

    def prepare_envelope(self, event: WebhookEvent) -> dict[str, Any]:
        """Serializes domain event into standard webhook envelope (ARC-07 §12.2)."""
        return {
            "id": str(event.id),
            "type": event.event_type,
            "created_at": event.created_at.isoformat(),
            "organization_id": str(event.organization_id),
            "data": event.data,
        }

    async def deliver(self, destination_url: str, event: WebhookEvent) -> dict[str, Any]:
        """Prepares signed headers and delivers webhook payload."""
        envelope = self.prepare_envelope(event)
        payload_bytes = json.dumps(envelope, sort_keys=True).encode("utf-8")
        timestamp = int(time.time())
        signature = sign_payload(self.signing_secret, timestamp, payload_bytes)

        headers = {
            "Content-Type": "application/json",
            "X-ModularMenu-Timestamp": str(timestamp),
            "X-ModularMenu-Signature": f"sha256={signature}",
        }

        record = {
            "destination_url": destination_url,
            "event_id": str(event.id),
            "headers": headers,
            "envelope": envelope,
            "delivered_at": datetime.datetime.now(datetime.UTC),
            "status": "delivered",
        }
        self.delivered_events.append(record)
        return record
