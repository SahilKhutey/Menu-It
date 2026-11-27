# FCD14-ADR-007: Transactional Outbox for FCD-14 Domain Events

## Status
Accepted

## Context
Downstream modules (menu indexing, analytics, notifications, billing) need reliable events when organizations, restaurants, branches, or memberships change.

## Decision
Publish all FCD-14 domain events through `OutboxEventPublisher` (FCD-10) within the same database transaction as the ORM state change.

## Consequences
- Prevents dual-write inconsistencies between PostgreSQL state and Redis/worker event consumers.
