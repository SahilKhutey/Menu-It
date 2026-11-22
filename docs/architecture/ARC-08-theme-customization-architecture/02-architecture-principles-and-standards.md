# ARC-08 §2 — Architecture Principles & Standards

## 1. Architectural Principles
1. **Configuration Over Code:** Restaurant visual presentation is dictated entirely by structured data documents, never template forks or ad-hoc stylesheets.
2. **Deterministic Resolution:** Given base theme $T$ and override document $O$, resolved style tokens $R$ are deterministically computed without side effects:
   $$R = \text{DeepMerge}(T, O)$$
3. **Slot-Based Component Composition:** Menu layouts define structured semantic slots (`header`, `navigation`, `category.header`, `category.items`, `footer`). Components may only be placed in declared compatible slots.
4. **Defense in Depth Security:** Strict whitelist validation on tokens, prop schemas, and layout pairs. Zero tolerance for HTML tags, inline scripts, JavaScript URLs (`javascript:`), or unbounded JSON trees.
5. **Portability & Headless Ready:** Customization documents are completely portable and decoupled from the persistence engine, ready for mobile apps, SSR, and third-party syndication.
