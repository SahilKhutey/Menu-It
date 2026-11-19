# ModularMenu — Architecture Compliance Checklist

**Document ID:** GOV-CHK-01  
**Status:** Approved  
**Governing Standard:** ARC-02 §16 (Completion & Approval Criteria)

Before any pull request, module implementation, or infrastructure change is approved and merged into `develop` or `main`, the author and reviewer must verify compliance against every mandatory item below.

---

## 1. Governing Principles Verification (P-01 to P-10)

| ID | Principle | Compliance Check | Verified? |
| :--- | :--- | :--- | :--- |
| **P-01** | **Modularity** | Feature resides strictly within its domain module; exposes explicit interface; no circular imports. | [ ] |
| **P-02** | **Separation of Concerns** | Clear boundary between API, Application, Domain, and Infrastructure layers. Domain has zero infrastructure imports. | [ ] |
| **P-03** | **Configuration-Driven Customization** | Zero code forks or custom CSS patches. Visual differentiation is 100% driven by JSON design tokens. | [ ] |
| **P-04** | **Multi-Tenant Isolation** | Every protected query explicitly filters by `restaurant_id`; tenant isolation tests pass. | [ ] |
| **P-05** | **Content & Presentation Independence** | Modifying dish data never mutates theme; changing theme never mutates catalog items. | [ ] |
| **P-06** | **Renderer Independence** | Customer menu renderer is completely decoupled from visual studio authoring code. | [ ] |
| **P-07** | **Immutable Publication** | Diners read frozen, compiled JSON snapshots with SHA-256 checksums; published records are strictly write-once. | [ ] |
| **P-08** | **Deployment Portability** | Runs with identical container binary across Managed SaaS and Customer-Hosted Docker profiles. | [ ] |
| **P-09** | **Secure by Design** | Authentication and authorization enforced on every private route; no sensitive secrets in repository. | [ ] |
| **P-10** | **Progressive Extensibility** | Custom components are allowlisted and contract-validated; no arbitrary user-uploaded script execution. | [ ] |

---

## 2. Architectural Constraints Verification (CON-01 to CON-16)

| ID | Architectural Constraint | Rule Enforced | Verified? |
| :--- | :--- | :--- | :--- |
| **CON-01** | Zero Code Forks | Prohibits client-specific branches or forks. | [ ] |
| **CON-02** | No Direct Database Queries from Frontend | Next.js frontend interacts strictly via versioned REST APIs. | [ ] |
| **CON-03** | No Synchronous Relational Joins on Diner Read Path | Public diner requests query pre-compiled snapshots only. | [ ] |
| **CON-04** | No Implicit Lazy Loading | SQLAlchemy relationships use `lazy="raise"` or explicit joins. | [ ] |
| **CON-05** | No Floating-Point Currency Types | Monetary values use `NUMERIC(12,2)` or integer minor units. | [ ] |
| **CON-06** | No Cross-Tenant Relational Foreign Keys | Foreign keys cannot span across multiple restaurant tenants. | [ ] |
| **CON-07** | Published Snapshots Are Immutable | Update/Delete operations on published versions are blocked. | [ ] |
| **CON-08** | Standardized Error Envelope | All API errors return RFC 7807 `application/problem+json`. | [ ] |
| **CON-09** | No Arbitrary Code Execution in Renderer | Dynamic theme/component rendering uses schema-validated tokens only. | [ ] |
| **CON-10** | Dual-Model Binary Invariant | Zero profile-specific application code branching. | [ ] |
| **CON-11** | Zero Mandatory Login for Diners | Dining guests can view menus without accounts or authentication. | [ ] |
| **CON-12** | Diner JavaScript Budget | Customer menu JS bundle size strictly below 120 KB gzip. | [ ] |
| **CON-13** | Timezone Uniformity | All database timestamps stored in UTC (`TIMESTAMPTZ`). | [ ] |
| **CON-14** | Primary Key Cryptographic Randomness | Persistent IDs are UUIDv4; public slugs match strict regex. | [ ] |
| **CON-15** | Design Token Mapping via CSS Variables | Themes compile to standard `--theme-*` custom properties. | [ ] |
| **CON-16** | OpenAPI Contract Alignment | Every endpoint has a traceable, validated Pydantic schema. | [ ] |

---

## 3. Reviewer Sign-Off Checklist

- [ ] Automated CI test suite passes with 0 failures (`pytest tests/`).
- [ ] Automated architecture boundary check passes with 0 violations (`pytest tests/architecture/`).
- [ ] Code formatting & linting clean (`ruff check`, `ruff format --check`, `npm run lint`).
- [ ] Database migrations tested up and down safely.
- [ ] Relevant ADR created and recorded in `docs/decisions/decision-register.md`.
