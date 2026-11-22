# ARC-09 §17 — Multilingual & Locale Formatting

## 1. Unicode & Script Support
Menu rendering fully supports complex Unicode scripts:
- Devanagari (Hindi, Marathi, Sanskrit)
- Latin extended (French, Spanish, Italian accents)
- East Asian scripts (Japanese Kanji/Kana, Simplified Chinese)
- Emoji food iconography (🌶️, 🌿, 🥩, 🍷)

## 2. Locale-Aware Formatting
- Numbers, currencies, and dates conform to the restaurant's operational timezone (e.g. `Asia/Kolkata`) and ISO currency standards.
- RTL (right-to-left) document direction flags are supported for future Arabic/Hebrew localization.
