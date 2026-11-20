# 06 — Physical Database Schema

## 1. Database DDL Overview

The physical schema implements PostgreSQL 15+ standards:
- Primary keys use UUID.
- Foreign keys specify explicit `ON DELETE` rules (`CASCADE` or `RESTRICT`).
- Check constraints enforce enum-like statuses, positive sort orders, non-negative prices, and valid 3-letter currency codes.
- Unique partial indexes enforce single default price rules:
  `CREATE UNIQUE INDEX uq_item_prices_one_default ON item_prices (organization_id, restaurant_id, item_id) WHERE is_default = TRUE;`
