# ARC-08 §9 — Deterministic Theme Resolver

## 1. Mathematical Definition
The resolver is an idempotent, pure function:
$$f(D) = \{ \text{theme}: \{ \text{tokens}: R \}, \text{layout}: L, \text{components}: C \}$$
Where:
$$R = \text{DeepMerge}(T_{\text{base}}, D_{\text{overrides}})$$

## 2. Deep Merge Algorithm Rules
1. Primitive values (strings, numbers, booleans) in `overrides` overwrite base theme tokens.
2. Dictionaries/maps are merged recursively key by key.
3. Setting an override key to `null` or empty string resets that specific token to the base theme default.
4. Input objects are deeply cloned before processing; the source dictionary is never mutated.
5. Identical inputs evaluate to strictly identical token outputs ($f(D) \equiv f(D)$).

Both Python (`app.modules.customization.resolver`) and TypeScript (`packages/theme-engine`) implement this exact algorithm.
