# ARC-09 §18 — Monetary Formatting & Pricing

## 1. Monetary Data Integrity
Pricing values use exact decimal representations (`Decimal` in Python, integer minor units / formatted strings in TypeScript).
- **Non-Negativity**: Prices < 0.00 are rejected immediately by domain entities and validators (`ARC09-T011`).
- **Zero-Price Items**: Supported for complimentary items (e.g. `₹0`).

## 2. Standard Currency Formats
- `INR`: Symbol `₹` (e.g., `₹340`, `₹340.50`).
- `USD`: Symbol `$` (e.g., `$14.99`).
- `EUR`: Symbol `€` (e.g., `€12.50`).
- `GBP`: Symbol `£` (e.g., `£9.95`).
- Other ISO codes: Formatted as `{CODE} {amount}` (e.g. `AED 45.00`).
