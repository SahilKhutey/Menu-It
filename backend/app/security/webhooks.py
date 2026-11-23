"""
ModularMenu — Webhook Security Architecture (ARC-12 §11, ADR-0239).
Cryptographic HMAC verification, timestamp tolerance, and replay protection.
"""

import hashlib
import hmac
import time


def verify_webhook_signature(
    secret: bytes,
    payload: bytes,
    supplied_signature: str,
) -> bool:
    """Validate webhook payload HMAC-SHA256 signature in constant time."""
    if not secret or not payload or not supplied_signature:
        return False
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, supplied_signature)


class WebhookReplayGuard:
    """In-memory sliding event registry preventing webhook replay attacks."""

    def __init__(self, tolerance_seconds: float = 300.0) -> None:
        self.tolerance_seconds = tolerance_seconds
        self._seen_events: dict[str, float] = {}

    def is_valid_and_fresh(self, event_id: str, timestamp: float, now: float | None = None) -> bool:
        """Validate that timestamp is within tolerance window and event ID is unique."""
        current_time = now if now is not None else time.time()

        # Check timestamp drift
        if abs(current_time - timestamp) > self.tolerance_seconds:
            return False

        # Purge stale events older than tolerance window
        cutoff = current_time - self.tolerance_seconds
        self._seen_events = {eid: ts for eid, ts in self._seen_events.items() if ts > cutoff}

        # Check deduplication
        if event_id in self._seen_events:
            return False

        self._seen_events[event_id] = timestamp
        return True


default_webhook_guard = WebhookReplayGuard()
