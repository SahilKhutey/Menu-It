# FCD-06 §12 — Shared API Transport Contracts

## 1. Schema Architecture

Transport schemas define the wire format between clients and the backend. Located in `apps/api/src/menu_it/contracts/`:

### 1.1 Response Envelope (`common.py`)
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "a92e106c-...",
    "timestamp": "2026-11-24T10:30:00Z"
  }
}
```

### 1.2 Error Envelope (`errors.py`)
```json
{
  "code": "VALIDATION_FAILED",
  "message": "Payload failed validation",
  "details": [
    {
      "field": "primary_currency",
      "message": "Unsupported currency code",
      "code": "INVALID_CURRENCY"
    }
  ]
}
```

### 1.3 Pagination Envelope (`pagination.py`)
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 142,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  },
  "meta": { ... }
}
```

### 1.4 Restaurant Profile Contracts (`restaurant.py`)
- `TimeRangeDTO`: `{"opens_at": "09:00", "closes_at": "17:00"}`
- `DailyOperatingHoursDTO`: `{"weekday": 1, "weekday_name": "MONDAY", "is_closed": false, "time_ranges": [...]}`
- `RestaurantProfileResponse`: Complete metadata response.
- `RestaurantProfileUpdateRequest`: Partial update payload.
