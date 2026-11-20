# 20 — Data Validation Rules

## 1. Multi-Tier Validation

1. **Client / UI:** Real-time user feedback.
2. **API / Pydantic:** Request schema validation and format sanitization.
3. **Application / Domain:** Business rules and invariants.
4. **Database Constraints:** Final referential integrity, unique constraints, and check constraints.
