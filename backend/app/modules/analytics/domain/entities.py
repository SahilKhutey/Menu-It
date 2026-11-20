"""
Analytics & Integrations Domain Entities (ARC-04 §6.16, MOD-16).
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


@dataclass
class UsageEvent:
    event_id: UUID
    restaurant_id: UUID
    event_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AnalyticsTracker:
    processed_event_ids: set[UUID] = field(default_factory=set)

    def record_event(self, event: UsageEvent) -> bool:
        """
        Records event with idempotency protection.
        Returns True if newly recorded, False if duplicate.
        """
        if event.event_id in self.processed_event_ids:
            return False  # Deduplicated
        self.processed_event_ids.add(event.event_id)
        return True
