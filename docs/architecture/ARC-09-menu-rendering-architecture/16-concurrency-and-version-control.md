# ARC-09 §16 — Concurrency & Version Control

## 1. Concurrency Model
The rendering engine operates statelessly. Multiple concurrent requests never contend on shared locks or database write transactions.
- Tested under 50 simultaneous public render calls with zero race conditions (`ARC09-T110`).
- Database reads occur in read-only isolation without acquiring table or row locks.

## 2. Version Immutability
Each published snapshot is assigned a monotonically increasing integer `version_number` and a SHA-256 `checksum`.
- Previous snapshots remain preserved and immutable in the `menu_versions` table.
- Fast rollback or historical review reads earlier versions without re-rendering.
