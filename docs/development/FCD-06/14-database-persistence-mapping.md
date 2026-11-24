# FCD-06 §14 — Database Persistence & Mapping

## 1. Relational Schema (`restaurant_profiles`)

Located in `apps/api/src/menu_it/database/models/restaurant_profile.py`:

```
+-------------------------------------------------------------+
|                      restaurant_profiles                    |
+-------------------------------------------------------------+
| id                  | UUID (PK)                             |
| organization_id     | UUID (FK -> organizations.id)         |
| restaurant_id       | UUID (FK -> restaurants.id, UNIQUE)   |
| public_name         | VARCHAR(255)                          |
| legal_name          | VARCHAR(255) NULL                     |
| description         | TEXT NULL                             |
| email               | VARCHAR(255) NULL                     |
| phone               | VARCHAR(32) NULL                      |
| address_line_1      | VARCHAR(255) NULL                     |
| address_line_2      | VARCHAR(255) NULL                     |
| address_locality    | VARCHAR(100) NULL                     |
| address_admin_area  | VARCHAR(100) NULL                     |
| address_postal_code | VARCHAR(20) NULL                      |
| address_country_code| VARCHAR(2) NULL                       |
| primary_currency    | VARCHAR(3) DEFAULT 'USD'              |
| timezone            | VARCHAR(64) DEFAULT 'UTC'             |
| schedule_payload    | JSONB NULL                            |
| website_url         | VARCHAR(2048) NULL                    |
| logo_asset_id       | UUID NULL                             |
| banner_asset_id     | UUID NULL                             |
| version             | INTEGER DEFAULT 1                     |
| created_at          | TIMESTAMPTZ DEFAULT now()             |
| updated_at          | TIMESTAMPTZ DEFAULT now()             |
+-------------------------------------------------------------+
| CONSTRAINTS:                                                |
| - uq_restaurant_profiles_restaurant_id (UNIQUE)             |
| - fk_restaurant_profiles_org_restaurant:                   |
|   (organization_id, restaurant_id)                          |
|     -> restaurants(organization_id, id) ON DELETE CASCADE   |
+-------------------------------------------------------------+
```

## 2. Mapper Architecture

`RestaurantProfileMapper` (`apps/api/src/menu_it/infrastructure/mappers/restaurant_profile_mapper.py`) performs bi-directional translation:
- `to_domain(record)`: Unpacks primitive columns and JSON schedule payload into immutable domain Value Objects (`Currency`, `TimeZone`, `Address`, `WeeklyOperatingSchedule`).
- `to_record(domain, existing)`: Flattens domain Value Objects into database columns, preparing updates without exposing persistence models to the domain.
