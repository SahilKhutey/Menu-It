# ARC-10 §9: Publication Validation Engine
**Multi-Stage Pre-Flight Verification**

## 1. Validation Categories
- **Content:** Menu title present, category titles present, no duplicate item IDs.
- **Pricing:** Non-negative item prices (`>= 0.0`), valid ISO currency code (`USD`, `EUR`, `INR`, etc.).
- **Availability:** Valid availability status.
- **Media:** Valid media asset URLs; missing optional images emit `WARNING`.
- **Presentation:** Theme and layout compatibility with pinned renderer contract.
- **Public Safety:** Rejection of private credentials or leaked tokens.

## 2. Diagnostics & Severity
- **ERROR:** Blocks publication immediately (`PUBLICATION_VALIDATION_FAILED`).
- **WARNING:** Informational; allowed to proceed under standard restaurant policy.
- **INFO:** Design and optimization suggestions.
