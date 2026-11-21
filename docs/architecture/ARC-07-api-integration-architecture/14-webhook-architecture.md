# 14. Webhook Architecture

## 1. Outbound Webhook Delivery
Outbound events (`menu.published`, `menu.rolled_back`, `item.availability_changed`) are persisted to the `outbox_events` table within the business database transaction.
An asynchronous worker dispatches events with HMAC-SHA256 signatures (`X-ModularMenu-Signature`).
