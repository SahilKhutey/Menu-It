# ARC-10 §7: Snapshot Architecture & Hashing
**Public Allowlist, Dependency Pinning, and Cryptographic Digests**

## 1. Public Field Allowlist
To prevent leaking sensitive internal data, the snapshot builder applies a strict allowlist:
- **Included:** Restaurant display name, description, logo, contact; menu title, description, currency; categories, sort orders; food item names, descriptions, prices, availability, spice levels, allergens, media references; presentation theme and layout tokens.
- **Excluded:** Internal administrative notes, soft-deleted flags, billing identifiers, user session tokens, passwords, API keys, profit margins.

## 2. Dependency Pinning
A snapshot pins exact presentation dependencies:
- `theme_id` and `theme_version` (e.g. `modern_clean` @ `1.0.0`)
- `layout_id` and `layout_version` (e.g. `category_first` @ `1.0.0`)
- `renderer_contract_version` (e.g. `1.0`)

## 3. Canonical SHA-256 Digest
Snapshots are serialized using stable key ordering, UTF-8 normalization, and standard monetary formatting:
```python
canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
content_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```
