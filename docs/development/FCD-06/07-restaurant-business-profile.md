# FCD-06 §07 — Restaurant Business Profile Aggregate

## 1. Aggregate Architecture

`RestaurantProfile` is the aggregate root governing a restaurant location's customer-facing metadata, branding, contact channels, physical address, and operating hours.

Located in `apps/api/src/menu_it/domain/restaurant/profile.py`.

## 2. Model Structure

```python
@dataclass(eq=False)
class RestaurantProfile(AggregateRoot):
    restaurant_id: UUID
    organization_id: UUID
    public_name: str
    primary_currency: Currency
    timezone: TimeZone
    legal_name: str | None = None
    description: str | None = None
    email: EmailAddress | None = None
    phone: PhoneNumber | None = None
    address: Address | None = None
    schedule: WeeklyOperatingSchedule | None = None
    website_url: str | None = None
    logo_asset_id: UUID | None = None
    banner_asset_id: UUID | None = None
    version: int = 1
    created_at: datetime = ...
    updated_at: datetime = ...
```

## 3. Explicit Mutation Methods

State changes are guarded by dedicated domain mutation methods that enforce validation and record domain events:

| Method | Behavior & Event Emitted |
| :--- | :--- |
| `create(...)` | Factory method generating aggregate with version 1; records `RestaurantProfileUpdated(changed_fields=('__created__',))` |
| `update_public_name(new_name)` | Validates non-empty trimmed string; increments version; records `RestaurantProfileUpdated` |
| `update_legal_name(new_legal_name)` | Updates legal entity title; increments version; records `RestaurantProfileUpdated` |
| `update_description(new_desc)` | Updates bio/marketing text; increments version; records `RestaurantProfileUpdated` |
| `update_contact(email, phone)` | Validates value objects; increments version; records `RestaurantProfileUpdated` |
| `update_address(address)` | Updates physical address; increments version; records `RestaurantProfileUpdated` |
| `update_localization(currency, tz)` | Updates Currency & TimeZone; increments version; records `RestaurantProfileUpdated` |
| `update_website_url(url)` | Updates website link; increments version; records `RestaurantProfileUpdated` |
| `update_media(logo_id, banner_id)` | Updates asset UUIDs; increments version; records `RestaurantProfileUpdated` |
| `update_schedule(new_schedule)` | Sets weekly operating hours; increments version; records `RestaurantOperatingHoursUpdated` and `RestaurantProfileUpdated` |

## 4. Optimistic Concurrency Control

Every mutation increments `self.version`. Persistence adapters verify that the database record version matches the expected aggregate state prior to mutation, preventing lost updates in concurrent workflows.
