# 04. API Request and Response Contracts

## 1. Schema Design Principles
All request bodies and responses are defined via Pydantic v2 schemas configured with strict typing:
- Request schemas use `ConfigDict(extra="forbid")` to reject unknown fields.
- Response schemas use `ConfigDict(from_attributes=True)` to map directly from ORM entities.
- Monies are stored and exposed in decimal units (e.g. `250.00`) and mapped to minor units internally (e.g. `25000` paise/cents).

## 2. Standard Envelope vs Direct Representation
- Entity collections return standard lists or paginated envelopes with cursor metadata.
- Single entity endpoints return direct JSON object representations matching declared schemas.
