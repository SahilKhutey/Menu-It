# ARC-07: API & Integration Architecture

## Document Metadata
- **Standard Baseline:** ARC-07
- **Version:** 1.0.0-arc07
- **Status:** Approved Baseline & Fully Implemented
- **Verification Status:** 75/75 Test Scenarios Passing (100%)
- **Parent Documents:** ARC-01 through ARC-06
- **Architecture Style:** Contract-First Modular Monolith REST API with Versioned Endpoints, Server-Derived Tenant Authorization, and Provider Adapters

## Executive Summary
ARC-07 establishes the formal contracts, protocols, and integration boundaries for ModularMenu. It guarantees that all internal module interactions, frontend applications, visual editors, public menu consumers, and third-party integrations operate under strictly validated, versioned, and tenant-safe RESTful API contracts.

## Architecture Documents in this Series
1. [01. API Architecture Overview](01-api-architecture-overview.md)
2. [02. API Design Standards](02-api-design-standards.md)
3. [03. API Resource Catalogue](03-api-resource-catalogue.md)
4. [04. API Request and Response Contracts](04-api-request-response-contracts.md)
5. [05. API Error Handling Architecture](05-api-error-handling.md)
6. [06. API Versioning and Compatibility](06-api-versioning-and-compatibility.md)
7. [07. Authentication Architecture](07-authentication-architecture.md)
8. [08. Authorization and Permissions Architecture](08-authorization-and-permissions.md)
9. [09. Tenant Context Integration](09-tenant-context-integration.md)
10. [10. Pagination, Filtering, and Search](10-pagination-filtering-and-search.md)
11. [11. Concurrency and Idempotency Architecture](11-concurrency-and-idempotency.md)
12. [12. Internal Module Integration](12-internal-module-integration.md)
13. [13. External Integration Architecture](13-external-integration-architecture.md)
14. [14. Webhook Architecture](14-webhook-architecture.md)
15. [15. Frontend API Integration](15-frontend-api-integration.md)
16. [16. OpenAPI and Contract Generation](16-openapi-and-contract-generation.md)
17. [17. Public Menu API Architecture](17-public-menu-api.md)
18. [18. Media API Architecture](18-media-api.md)
19. [19. Rate Limiting and Resource Protection](19-rate-limiting-and-resource-protection.md)
20. [20. API Security Requirements](20-api-security-requirements.md)
21. [21. API Observability and Telemetry](21-api-observability.md)
22. [22. API Testing Strategy](22-api-testing-strategy.md)
23. [23. Verification and Validation](23-verification-and-validation.md)
24. [24. Implementation Work Packages](24-implementation-work-packages.md)
25. [25. API Risk Register](25-api-risk-register.md)
26. [26. Architecture Decision Records](26-architecture-decision-records.md)
27. [27. Architecture Compliance Report](27-architecture-compliance-report.md)

## Key Technical Specifications
- **REST Endpoints Registered:** 66 OpenAPI endpoints across 10 functional tag categories.
- **Error Model:** RFC 7807 / RFC 9457 Problem Details with machine-parseable error codes and field-level validation errors.
- **Tenant Context:** Derivation strictly from server-side cryptographic sessions and database memberships. Client-supplied headers treated strictly as selectors.
- **Optimistic Concurrency:** HTTP ETag / If-Match and row_version tracking preventing silent overwrites.
- **Reliable Webhooks:** HMAC-SHA256 signed payloads with transactional outbox persistence and exponential backoff retry.
