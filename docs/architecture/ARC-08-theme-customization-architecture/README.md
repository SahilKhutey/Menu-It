# ARC-08 — Theme & Customization Architecture Documentation Suite

## Overview
This documentation suite establishes the formal engineering baseline, specifications, contracts, and verification procedures for **ModularMenu's Theme & Customization Architecture** (`ARC-08`).

| Document Property | Definition |
| :--- | :--- |
| **System** | ModularMenu / Menu-It |
| **Document ID** | ARC-08 Series |
| **Version** | 1.0.0-arc08 |
| **Status** | Approved Engineering Baseline |
| **Parent Documents** | ARC-01, ARC-02, ARC-03, ARC-04, ARC-05, ARC-06, ARC-07 |
| **Downstream Documents** | ARC-09 (Menu Rendering), ARC-10 (Publishing & Versioning) |
| **Primary Architecture Model** | Modular Monolith (Shared-SaaS & Customer-Hosted) |
| **Automated Test Matrix** | 104 Scenarios (104/104 Passing, 100% Pass Rate) |
| **Decisions Recorded** | ADR-0114 through ADR-0140 (27 Architectural Decisions) |

---

## Document Index

1. [01. Architecture Overview](./01-theme-architecture-overview.md)
2. [02. Principles & Standards](./02-architecture-principles-and-standards.md)
3. [03. Lifecycle & State Machine](./03-customization-lifecycle-and-state-machine.md)
4. [04. Design Token Architecture](./04-design-token-architecture.md)
5. [05. Platform Theme Catalogue](./05-platform-theme-catalogue.md)
6. [06. Platform Layout Catalogue](./06-platform-layout-catalogue.md)
7. [07. Component Registry & Slots](./07-component-registry-and-slot-architecture.md)
8. [08. Customization Document Spec](./08-menu-customization-document-specification.md)
9. [09. Deterministic Theme Resolver](./09-deterministic-theme-resolver.md)
10. [10. CSS Variable & Style Generation](./10-css-variable-and-style-generation.md)
11. [11. Validation Pipeline](./11-customization-validation-pipeline.md)
12. [12. Concurrency & Versioning](./12-optimistic-concurrency-and-versioning.md)
13. [13. API Specification](./13-customization-api-specification.md)
14. [14. Revision History & Audit Trail](./14-revision-history-and-audit-trail.md)
15. [15. Settings Editor Architecture](./15-settings-editor-architecture.md)
16. [16. Visual Editor Architecture](./16-visual-editor-architecture.md)
17. [17. Editor History & Undo/Redo](./17-editor-history-and-undo-redo.md)
18. [18. Public Menu Rendering Integration](./18-public-menu-rendering-integration.md)
19. [19. Security & Tenant Isolation](./19-security-and-tenant-isolation.md)
20. [20. Performance & Caching Strategy](./20-performance-and-caching-strategy.md)
21. [21. Accessibility & Responsive Design](./21-accessibility-and-responsive-design.md)
22. [22. Testing Strategy & Test Matrix](./22-testing-strategy-and-test-matrix.md)
23. [23. Verification & Validation Criteria](./23-verification-and-validation-criteria.md)
24. [24. Implementation Work Packages](./24-implementation-work-packages.md)
25. [25. Risk Register & Mitigations](./25-risk-register-and-mitigations.md)
26. [26. Architecture Decision Records](./26-architecture-decision-records.md)
27. [27. Migration & Extensibility Guide](./27-migration-and-extensibility-guide.md)
28. [28. Compliance & Completion Report](./28-compliance-and-completion-report.md)
