# 13 — Public Menu Rendering Isolation

## 1. The Public/Private Boundary

Public diner endpoints (`/r/[slug]`) execute under a **Public Read Policy**, not an authenticated tenant session:
- Public endpoints **only resolve active published snapshots** (`MOD-13`).
- They never read draft tables (`MOD-12`), internal notes, or member rosters.
- Inactive or suspended restaurant menus return 404 or a standard grace notice.

## 2. Immutability

Published snapshots are immutable, SHA-256 verified JSON structures. Modifying a draft menu in the visual editor has zero impact on live diners until a new snapshot is published.
