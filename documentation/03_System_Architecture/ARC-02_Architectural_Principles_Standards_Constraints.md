ARC-02 — Architectural Principles, Standards & Design Constraints
Architecture Documentation
Proposed Baseline
Version 1.0

Project: ModularMenu
Document ID: ARC-02
Document Type: System Architecture — Principles, Standards & Constraints
Parent Document: ARC-01 — System Architecture Overview
Status: Approved Architectural Specification
Implementation Status: Formally Implemented & Verified (15/15 Checklist Complete)
Scope: All applications, modules, APIs, data structures, rendering systems, infrastructure adapters, and deployment editions.
1. Document purpose
ARC-02 establishes the engineering rules that govern how ModularMenu must be designed, developed, tested, deployed, maintained, and extended.

ARC-01 established the system's high-level architecture. ARC-02 converts that architecture into enforceable engineering standards.

The purpose is to prevent architectural inconsistency as the platform grows, particularly across:
- Multi-tenant SaaS and customer-hosted deployments.
- Restaurant management and menu administration.
- Theme, layout, and component customization.
- Visual editing and public menu rendering.
- Menu publication, versioning, and rollback.
- Authentication, authorization, and licensing.
- Shared infrastructure and deployment portability.
This document is intended to become a reference for every future implementation work package.
1.1 Primary objectives
1. Establish non-negotiable architectural principles.
2. Define approved design and development standards.
3. Establish boundaries between system layers and modules.
4. Define technology and implementation constraints.
5. Standardize API, database, security, frontend, and backend practices.
6. Define automated enforcement mechanisms.
7. Establish architectural review and approval procedures.
8. Define test cases and acceptance criteria.
9. Establish verification and validation procedures.
10. Prevent uncontrolled technical complexity and architectural drift.
1.2 Document applicability
Area	Applicability
Backend	Mandatory
Frontend	Mandatory
Database	Mandatory
Theme engine	Mandatory
Layout engine	Mandatory
Component registry	Mandatory
Menu renderer	Mandatory
Visual editor	Mandatory
Publishing engine	Mandatory
SaaS infrastructure	Mandatory
Customer-hosted edition	Mandatory
External integrations	Mandatory
CI/CD and testing	Mandatory


2. Architectural governance model
Before defining the engineering rules, ModularMenu needs a mechanism for controlling architectural decisions.

Without governance, different developers may independently introduce incompatible patterns, libraries, database structures, or deployment approaches.
2.1 Architectural decision hierarchy
All technical decisions must follow this hierarchy:
Level 1 — System Architecture

ARC-01 to ARC-12: system-wide architecture and boundaries


Level 2 — Architectural Standards

ARC-02: principles, standards, constraints and governance


Level 3 — Module Architecture

Module specifications, interfaces, responsibilities and contracts


Level 4 — Implementation

Source code, configuration, migrations, tests and deployment


A lower-level implementation must not silently override an approved higher-level architectural decision.
2.2 Architectural decision records (ADR)
Every significant architectural decision must be documented.

Examples:
- Selecting a new backend framework.
- Changing database technology.
- Introducing a new caching system.
- Changing tenant isolation strategy.
- Introducing a new component-rendering mechanism.
- Changing publication consistency guarantees.
- Adding an external authentication provider.
- Changing the deployment architecture.
Each decision must have:
Field	Required content
ADR ID	Unique decision identifier
Title	Decision subject
Status	Proposed, Accepted, Rejected, Superseded
Context	Why a decision is necessary
Problem	The issue being addressed
Options	Available alternatives
Decision	Selected approach
Rationale	Technical and business justification
Consequences	Benefits, limitations and risks
Validation	How the decision will be tested
References	Related architecture documents

Naming convention: ADR-001, ADR-002, ADR-003, and so on.
2.3 Architectural decision statuses
- Proposed: awaiting review.
- Accepted: approved for implementation.
- Rejected: explicitly not selected.
- Superseded: replaced by a newer decision.
- Deprecated: no longer recommended, but potentially still present.
No major architecture decision should exist only in chat messages, informal discussions, or developer assumptions.

3. Core architectural principles
These principles define how ModularMenu must behave as a software system.

Each principle includes its purpose, implementation rules, prohibited approaches, and verification requirements.
3.1 Principle P-01 — Modularity
Objective: Keep system responsibilities separated into independently understandable and maintainable modules.

Implementation requirements:
1. Each module must have one clearly defined business responsibility.
2. Each module must expose an explicit interface.
3. Modules must not access another module's internal implementation directly.
4. Shared functionality must be placed in explicitly governed shared packages.
5. Modules must have documented dependencies.
6. Circular dependencies are prohibited.
7. Module-specific validation and business rules must remain within their appropriate boundaries.
Example:
backend/
├── app/
│   ├── modules/
│   │   ├── identity/
│   │   ├── tenants/
│   │   ├── restaurants/
│   │   ├── menus/
│   │   ├── categories/
│   │   ├── menu_items/
│   │   ├── themes/
│   │   ├── layouts/
│   │   ├── components/
│   │   ├── publishing/
│   │   └── licensing/
│   │
│   ├── shared/
│   │   ├── database/
│   │   ├── security/
│   │   ├── exceptions/
│   │   └── observability/
│   │
│   └── main.py


Prohibited:
# Prohibited architectural couplingfrom app.modules.menus.internal_repository import MenuRepositoryfrom app.modules.publishing.internal_service import PublishingService



The preferred approach is to communicate through a public application service or defined interface.

Verification:
- No circular module dependencies.
- No unauthorized internal imports.
- Every module has a documented responsibility.
- Module tests can execute without starting the entire platform.
3.2 Principle P-02 — Separation of concerns
Objective: Ensure that business logic, data access, API handling, and presentation are not mixed together.

The backend must distinguish:
Layer	Responsibility
API / Presentation	HTTP requests, responses, input parsing
Application	Use-case orchestration
Domain	Business rules and invariants
Infrastructure	Database, storage, email and external services

Example:
modules/menus/
├── api/
│   └── routes.py
├── application/
│   ├── create_menu.py
│   └── publish_menu.py
├── domain/
│   ├── entities.py
│   ├── rules.py
│   └── exceptions.py
├── infrastructure/
│   └── repositories.py
└── schemas/
    └── menu_schemas.py


Rules:
- API routes must not contain substantial business logic.
- Database queries must not be embedded in frontend components.
- Domain entities must not depend on FastAPI or HTTP request objects.
- External service calls must use infrastructure adapters.
- The renderer must not depend on dashboard UI components.
Verification: Inspect the dependency graph and test business use cases independently of HTTP and database infrastructure.
3.3 Principle P-03 — Configuration-driven customization
Objective: Allow restaurants to customize their menus without modifying platform source code.

Restaurant-specific appearance and layout must be driven by validated configuration.

The configuration model must support:
1. Design tokens.
2. Theme selection.
3. Layout selection.
4. Component configuration.
5. Component visibility.
6. Menu presentation settings.
7. Responsive behavior.
8. Supported language and display preferences.
Illustrative configuration:
{
  "schema_version": 1,
  "theme": {
    "preset": "modern",
    "tokens": {
      "primary": "#1E293B",
      "background": "#FFFFFF",
      "surface": "#F8FAFC",
      "radius": "12px"
    }
  },
  "layout": {
    "type": "grid",
    "columns": {
      "mobile": 1,
      "tablet": 2,
      "desktop": 3
    }
  },
  "components": [
    {
      "type": "menu-header",
      "enabled": true
    },
    {
      "type": "category-navigation",
      "enabled": true
    },
    {
      "type": "menu-item-card",
      "enabled": true
    }
  ]
}


Rules:
- Configuration must have a versioned schema.
- Unknown component types must be rejected or safely ignored according to the relevant contract.
- Invalid configuration must never reach the production renderer unchecked.
- Arbitrary JavaScript execution must not be permitted.
- Configuration migration must be supported when schemas evolve.
Verification: Change theme, layout, and component settings without modifying application source code; confirm the published menu reflects the validated configuration.
3.4 Principle P-04 — Multi-tenant isolation
Objective: Ensure that each restaurant can access only the information and operations it is authorized to use.

Mandatory controls:
- Server-side tenant resolution.
- Tenant-scoped authorization.
- Tenant-aware database queries.
- PostgreSQL Row-Level Security as an additional safeguard.
- Tenant-aware cache keys.
- Tenant-scoped media authorization.
- Tenant-aware audit records.
- Tenant-isolation integration tests.
Example:
def get_menu(    menu_id: UUID,    tenant_id: UUID,    repository: MenuRepository):    return repository.get_by_id_and_tenant(        menu_id=menu_id,        tenant_id=tenant_id    )



Never rely on a frontend-supplied tenant ID as proof of authorization.

A request for a resource belonging to another tenant must not return its private data.

Verification: Execute cross-tenant access tests against every protected resource and operation.
3.5 Principle P-05 — Content and presentation independence
Objective: Separate restaurant menu data from the way the menu is visually presented.

Content includes:
- Menu name.
- Category name.
- Food item name.
- Description.
- Price.
- Availability.
- Images.
- Variants and add-ons.
- Translations.
Presentation includes:
- Colors.
- Typography.
- Spacing.
- Layout.
- Component structure.
- Visual behavior.
- Responsive rules.
A food item must not contain hardcoded presentation logic.

Example:
{
  "id": "item-001",
  "name": "Paneer Tikka",
  "description": "Grilled paneer with spices",
  "price_minor": 24900,
  "currency": "INR"
}


The renderer decides how this data appears based on the restaurant's theme and layout configuration.

Verification: Render the same menu content through at least three different themes without altering the underlying menu records.
3.6 Principle P-06 — Renderer independence
The public menu rendering engine must operate independently of the restaurant administration interface.

Requirements:
- Renderer consumes published menu data and presentation configuration.
- Renderer does not require dashboard state.
- Renderer does not require an authenticated restaurant user.
- Renderer must not access unpublished drafts.
- Renderer must support responsive presentation.
- Renderer must validate component configuration.
- Renderer must handle missing optional assets gracefully.
Verification: Build and test the public menu route without loading the dashboard application or editor state.
3.7 Principle P-07 — Immutable publication
Once a menu version is published, its snapshot must not be modified in place.

Requirements:
1. Drafts remain editable.
2. Publication creates a new version.
3. Published snapshots are immutable.
4. Each version has a unique identifier.
5. The active publication points to a specific version.
6. Rollback changes the active version reference.
7. Old versions remain available according to the retention policy.
Example:
Draft
  |
  v
Validation
  |
  v
Snapshot Creation
  |
  v
Version 1
  |
  v
Published
  |
  v
Draft Updated
  |
  v
Version 2
  |
  v
Published


Version 1 must remain unchanged after Version 2 is published.

Verification: Compare snapshot hashes before and after subsequent publications; confirm historical snapshots remain unchanged.
3.8 Principle P-08 — Deployment portability
The platform must not depend on one hosting provider's proprietary features for core business logic.

Requirements:
- Container-compatible services.
- Environment-based configuration.
- Storage abstraction.
- Database configuration through supported connection settings.
- Provider-independent application services.
- Documented installation and backup procedures.
- Shared application code across managed and self-hosted editions.
Verification: Run the application using a local Docker Compose deployment and a managed-environment configuration without changing core business logic.
3.9 Principle P-09 — Secure by design
Security must be implemented at the architecture and domain levels, not added only before release.

Mandatory requirements:
- Secure authentication.
- Role-based authorization.
- Tenant isolation.
- Input validation.
- Output encoding.
- Secure session management.
- Upload validation.
- Rate limiting.
- Audit logging.
- Secret management.
- Dependency vulnerability checks.
- Backup and restore verification.
Verification: Security tests must cover authentication, authorization, tenant boundaries, input validation, uploads, and public endpoints.
3.10 Principle P-10 — Progressive extensibility
The system must support new modules and features without requiring a rewrite of existing modules.

Examples of future extensions:
- Multiple restaurant branches.
- Additional menu languages.
- Advanced analytics.
- Restaurant-specific domains.
- External POS integrations.
- Online ordering.
- Subscription tiers.
- Additional component types.
- New theme presets.
Rules:
- New features must use defined module interfaces.
- Existing API contracts must remain compatible where possible.
- Database changes must be migration-driven.
- New renderer components must use the component registry.
- Future functionality must not be introduced by uncontrolled conditional logic in unrelated modules.
Verification: Add a new theme preset and a new component type without modifying the menu data model or existing published snapshots.

4. System-wide engineering standards
This section establishes the concrete development standards that implement the principles.
4.1 Technology standards
The following is the proposed technology baseline inherited from ARC-01.
System area	Standard
Frontend	Next.js + React + TypeScript
UI styling	Tailwind CSS
Admin components	shadcn/ui
Backend	FastAPI
Backend language	Python
Data validation	Pydantic
ORM	SQLAlchemy
Database	PostgreSQL
Migrations	Alembic
Media storage	S3-compatible abstraction
Local development	Docker Compose
Backend testing	Pytest
Frontend testing	Vitest
Browser testing	Playwright
CI/CD	GitHub Actions
API style	REST
API prefix	/api/v1/

These are architecture-level selections, not a claim that every dependency has already been installed or validated.

Any proposed replacement requires an ADR.
Technology selection acceptance requirements
Before adding a major technology:
1. Identify the problem it solves.
2. Compare at least two viable approaches where appropriate.
3. Evaluate maintenance and licensing.
4. Evaluate security and update frequency.
5. Evaluate compatibility with the existing architecture.
6. Evaluate self-hosted deployment compatibility.
7. Document operational costs and complexity.
8. Record the decision in an ADR.
4.2 Backend coding standards
Naming conventions
Element	Convention	Example
Modules	snake_case	menu_items
Files	snake_case	menu_service.py
Classes	PascalCase	MenuService
Functions	snake_case	create_menu()
Constants	UPPER_SNAKE_CASE	MAX_UPLOAD_SIZE
Variables	snake_case	restaurant_id
Types	PascalCase	MenuCreate

Backend implementation rules
- Use Python type annotations.
- Use Pydantic models for external request and response validation.
- Use SQLAlchemy for database access.
- Use Alembic for database schema migrations.
- Use dependency injection for infrastructure services.
- Use explicit exception types.
- Use structured logging.
- Keep route handlers small.
- Avoid global mutable application state.
- Avoid synchronous blocking operations in asynchronous request paths.
- Avoid exposing ORM objects directly as public API responses.
Example:
from uuid import UUIDfrom pydantic import BaseModel, Fieldclass MenuCreate(BaseModel):    restaurant_id: UUID    name: str = Field(min_length=1, max_length=120)    description: str | None = Field(        default=None,        max_length=500    )class MenuResponse(BaseModel):    id: UUID    name: str    description: str | None    model_config = {        "from_attributes": True    }



The request's restaurant_id must still be checked against the authenticated user's permissions. Validation alone does not establish authorization.
4.3 Frontend coding standards
Component conventions
- Use TypeScript for application components.
- Prefer functional React components.
- Keep UI components focused on presentation.
- Use shared design tokens.
- Keep API communication in dedicated client/service modules.
- Avoid duplicating business rules in the browser.
- Use server-side authorization for protected operations.
- Use reusable components for repeated visual patterns.
- Avoid direct manipulation of the DOM unless required by a well-defined integration.
Suggested organization:
frontend/
├── app/
│   ├── platform/
│   ├── app/
│   └── r/
│
├── components/
│   ├── ui/
│   ├── shared/
│   └── layouts/
│
├── features/
│   ├── authentication/
│   ├── restaurants/
│   ├── menus/
│   ├── themes/
│   ├── editor/
│   └── publishing/
│
├── packages/
│   ├── design-tokens/
│   ├── theme-engine/
│   ├── menu-renderer/
│   ├── component-registry/
│   └── shared-types/
│
└── lib/
    ├── api/
    ├── validation/
    └── utilities/


Frontend quality rules
- No untyped any in production code without documented justification.
- No hardcoded tenant-specific branding.
- No hardcoded restaurant menu content in shared renderer components.
- No direct database access from browser components.
- No secrets in frontend environment variables.
- All interactive controls must have appropriate accessibility labels.
- Responsive behavior must be tested at defined viewport sizes.
- Loading, empty, error, and success states must be handled.
4.4 API design standards
All APIs must follow consistent naming, validation, error handling, and authorization rules.

Base path:
/api/v1/


Example endpoints:
POST   /api/v1/restaurants
GET    /api/v1/restaurants/{restaurant_id}

POST   /api/v1/menus
GET    /api/v1/menus/{menu_id}
PATCH  /api/v1/menus/{menu_id}
DELETE /api/v1/menus/{menu_id}

POST   /api/v1/menus/{menu_id}/publish
GET    /api/v1/menus/{menu_id}/versions
POST   /api/v1/menus/{menu_id}/rollback


Public endpoints:
GET /api/v1/public/restaurants/{slug}/menus/{menu_slug}


API rules:
1. Use HTTP methods according to operation semantics.
2. Use consistent status codes.
3. Validate all inputs.
4. Apply authorization on every protected request.
5. Return consistent error formats.
6. Use pagination for potentially large collections.
7. Use explicit response schemas.
8. Avoid exposing internal database identifiers or implementation details unnecessarily.
9. Use idempotency controls for operations where duplicate execution could cause harmful results.
10. Document API contracts using OpenAPI.
Suggested error structure:
{
  "error": {
    "code": "MENU_NOT_FOUND",
    "message": "The requested menu could not be found.",
    "request_id": "req-example-001"
  }
}


4.5 Database standards
Mandatory database conventions:
- UUID identifiers for externally referenced entities.
- Explicit foreign keys.
- Explicit unique constraints.
- Tenant-scoped indexes.
- UTC timestamps.
- Database migrations for every schema change.
- Transactional handling of critical operations.
- Integer minor units or NUMERIC for monetary values.
- No floating-point arithmetic for currency.
- JSONB only for genuinely flexible configuration.
- Immutable published snapshots.
- Documented retention and deletion rules.
Example monetary representation:
class MenuItem:    price_minor: int    currency: str = "INR"



For INR, 24900 represents ₹249.00 when the application uses two decimal places.

All price conversions must use an explicit currency precision policy rather than assuming every currency uses two decimal places.
Database migration rules
Every migration must:
1. Have a unique revision ID.
2. Have a descriptive name.
3. Define upgrade behavior.
4. Define downgrade behavior where safely possible.
5. Be tested against a representative database.
6. Preserve existing data.
7. Be reviewed for tenant-isolation implications.
8. Be included in deployment documentation.
Destructive changes require an explicit migration plan, backup strategy, and approval.

5. Architectural constraints and prohibited patterns
These are mandatory boundaries, not optional recommendations.
ID	Constraint	Prohibited behavior
CON-01	Shared core across editions	Separate SaaS and self-hosted business logic
CON-02	Tenant isolation	Trusting client-supplied tenant IDs
CON-03	Content/presentation separation	Embedding theme rules in menu records
CON-04	Renderer independence	Importing dashboard state into public renderer
CON-05	Immutable publication	Editing a published snapshot in place
CON-06	Validated components	Executing arbitrary user-supplied JavaScript
CON-07	Configuration portability	Hardcoding hosting-provider dependencies
CON-08	Layer separation	Business logic inside HTTP route handlers
CON-09	Controlled integrations	Direct external-provider calls throughout modules
CON-10	Secure secrets	Committing credentials or private keys
CON-11	Currency correctness	Using floating-point values for money
CON-12	Versioned APIs	Breaking public API contracts without versioning
CON-13	Migration discipline	Changing production schemas manually
CON-14	Access control	Relying on hidden frontend buttons as authorization
CON-15	Controlled extensibility	Unreviewed plugins with unrestricted execution
CON-16	Dependency control	Unapproved packages with unknown maintenance or license status

5.1 Prohibited architecture examples
Example A — Business logic in route handlers
@router.post("/menus")async def create_menu(request: MenuCreate):    # Prohibited: route contains authorization,    # database operations and business rules.    ...



Preferred:
@router.post("/menus")async def create_menu(    request: MenuCreate,    service: MenuApplicationService = Depends(        get_menu_service    )):    return await service.create_menu(request)



Example B — Frontend-only authorization
if (user.role === "owner") {
  showPublishButton();
}


This is acceptable as a UI visibility decision, but it is not authorization.

The backend must independently verify the user's permission before publishing.

Example C — Arbitrary component execution
// Prohibited: executing restaurant-provided code.
eval(componentConfiguration.code);


Instead, use an allowlisted component registry with validated properties.

6. Design standards for critical platform systems
The following rules are especially important because ModularMenu's main product value is customization through a reusable framework.
6.1 Theme engine standards
The theme engine must:
- Consume validated design tokens.
- Support theme presets.
- Support controlled restaurant overrides.
- Separate semantic tokens from raw CSS implementation.
- Support responsive presentation.
- Provide safe defaults.
- Reject invalid values.
- Avoid executing arbitrary CSS or JavaScript supplied by restaurants.
- Support theme schema versioning.
Proposed token categories:
colors/
├── primary
├── secondary
├── background
├── surface
├── text
├── muted
├── border
└── accent

typography/
├── font_family
├── heading_scale
├── body_scale
└── line_height

spacing/
├── compact
├── comfortable
└── spacious

shape/
├── radius
└── border_width

effects/
├── shadow
└── overlay


Acceptance test: Switching between theme presets must change visual presentation without changing menu content.
6.2 Layout engine standards
Supported initial layout types should be explicitly registered.

Proposed baseline:
- Grid.
- List.
- Image cards.
- Horizontal category navigation.
- Featured-item layout.
Rules:
- Layouts consume standardized menu data.
- Each layout must define supported configuration properties.
- Layouts must provide responsive behavior.
- Layouts must not change underlying menu content.
- Unsupported configurations must produce a controlled fallback or validation error.
- Layout configuration must be versioned.
Acceptance test: The same menu must render in at least three supported layouts with identical item names, descriptions, and prices.
6.3 Component registry standards
Each component definition must include:
Property	Purpose
Component ID	Stable identifier
Name	Human-readable name
Schema version	Configuration compatibility
Property schema	Allowed configuration
Default values	Safe initial state
Renderer mapping	Approved implementation
Responsive rules	Viewport behavior
Availability	Enabled/deprecated status
Compatibility	Supported renderer versions

Example conceptual definition:
{
  "id": "menu-item-card",
  "schema_version": 1,
  "properties": {
    "show_image": {
      "type": "boolean",
      "default": true
    },
    "show_description": {
      "type": "boolean",
      "default": true
    },
    "show_price": {
      "type": "boolean",
      "default": true
    }
  }
}


The actual schema must be validated server-side and, where appropriate, client-side using the same contract definitions.
6.4 Visual editor standards
The editor must follow a controlled configuration workflow:
Load Existing Configuration
          |
          v
Create Local Draft
          |
          v
Select Component
          |
          v
Edit Properties
          |
          v
Validate Configuration
          |
          v
Preview
          |
          v
Save Draft
          |
          v
Publish Through Publishing Workflow


Rules:
- The visual editor must not directly modify published snapshots.
- Every editable property must have a defined schema.
- Invalid configurations must be blocked from publication.
- The editor must support preview and cancel.
- The editor must distinguish unsaved, saved, and published states.
- The editor must handle stale draft conflicts.
- The editor must not expose arbitrary executable code.
6.5 Publishing standards
Publication must be treated as a critical business transaction.

Required behavior:
1. Identify the target draft.
2. Validate menu data.
3. Validate theme and layout configuration.
4. Validate component properties.
5. Generate a complete snapshot.
6. Persist the snapshot.
7. Atomically update the active publication reference.
8. Record publication metadata.
9. Invalidate relevant caches.
10. Return the published version identifier.
A failure before activation must not expose a partially published version.

A cache invalidation failure must be recoverable and must not silently change the identity of the published version.

7. Security and reliability design constraints
7.1 Authentication and authorization
The platform must distinguish:
- Authentication: who is making the request?
- Authorization: what is the user permitted to do?
- Tenant resolution: which organization or restaurant context applies?
The three operations must not be treated as interchangeable.
Minimum permission matrix
Operation	Owner	Manager	Menu Editor	Public Customer
View private dashboard	Yes	Yes	Yes	No
Edit restaurant profile	Yes	Configurable	No	No
Manage menu items	Yes	Yes	Yes	No
Edit themes	Yes	Yes	Configurable	No
Publish menu	Yes	Configurable	No by default	No
Manage members	Yes	Configurable	No	No
View published menu	Yes	Yes	Yes	Yes

Platform Owner and Platform Staff permissions must be separately governed and must not automatically grant unrestricted restaurant-level access without an explicit operational authorization mechanism.
7.2 Upload and media security
Media upload controls must include:
- Allowed MIME types.
- File size limits.
- File signature validation.
- Image dimension limits.
- Safe generated filenames.
- Malware scanning where operationally available.
- Metadata stripping where appropriate.
- Private object access controls.
- Public delivery through controlled media URLs.
- Tenant ownership checks.
7.3 Reliability constraints
The platform must provide:
- Health-check endpoints.
- Structured logs.
- Error tracking.
- Database backups.
- Backup restoration procedures.
- Safe retry behavior.
- Transaction management.
- Graceful degradation when optional integrations are unavailable.
- Monitoring of publication failures.
- Monitoring of storage and database failures.
Redis must remain optional in the initial architecture. The core menu platform must not stop functioning simply because an optional cache service is unavailable.

8. Documentation standards
All architecture and implementation documentation must use consistent structures.
8.1 Required documentation set
Document ID	Document	Purpose
DOC-STD-01	Coding Standards	Backend and frontend coding rules
DOC-STD-02	API Standards	Endpoint, response and error conventions
DOC-STD-03	Database Standards	Schema, indexing, migration and tenant rules
DOC-STD-04	Security Standards	Authentication, authorization and data protection
DOC-STD-05	Testing Standards	Testing levels and acceptance requirements
DOC-STD-06	Git & Branching Standards	Branching, commits and pull requests
DOC-STD-07	Dependency Standards	Dependency approval, updates and licensing
DOC-STD-08	Configuration Standards	Environment variables and configuration schemas
DOC-STD-09	Logging & Monitoring Standards	Observability and operational diagnostics
DOC-STD-10	Deployment Standards	Environment, release and rollback rules
DOC-STD-11	Architecture Decision Records	Significant architecture decisions
DOC-STD-12	Architecture Compliance Report	Evidence of adherence to approved architecture

8.2 Standard implementation document structure
Every module-level implementation document should contain:
1. Purpose.
2. Scope.
3. Module responsibility.
4. Architectural dependencies.
5. Functional requirements.
6. Technical design.
7. API contracts.
8. Data structures.
9. Security considerations.
10. Implementation tasks.
11. Test cases.
12. Verification procedure.
13. Validation criteria.
14. Deployment requirements.
15. Known limitations.
16. Acceptance criteria.
8.3 Documentation storage structure
docs/
├── architecture/
│   ├── ARC-01-system-overview.md
│   ├── ARC-02-principles-standards-constraints.md
│   ├── ARC-03-application-architecture.md
│   └── ...
│
├── standards/
│   ├── coding-standards.md
│   ├── api-standards.md
│   ├── database-standards.md
│   ├── security-standards.md
│   └── testing-standards.md
│
├── decisions/
│   ├── ADR-001-modular-monolith.md
│   └── ...
│
├── modules/
├── implementation/
├── testing/
├── deployment/
└── reports/



9. Git, version control and code review standards
9.1 Branching model
Proposed branches:
Branch	Purpose
main	Stable and release-ready
develop	Integration branch
feature/*	New feature development
fix/*	Defect correction
release/*	Release preparation
hotfix/*	Urgent production corrections

9.2 Commit convention
Use Conventional Commits.

Examples:
feat(menu): add category management

fix(auth): prevent cross-tenant access

docs(architecture): add ARC-02 standards

test(publishing): verify snapshot immutability

refactor(theme): isolate token resolution

chore(ci): enforce backend linting


9.3 Pull request requirements
Every pull request must include:
- Description of the change.
- Related issue or work package.
- Affected modules.
- Architecture impact.
- Database migration impact.
- Security impact.
- Automated test evidence.
- Manual verification evidence where needed.
- Documentation updates.
- Rollback considerations.
No pull request may be merged if mandatory CI checks fail.

For changes involving tenant isolation, publication, authorization, or database security, additional reviewer scrutiny is required.

10. Implementation and execution work packages
This section translates ARC-02 into actionable engineering work.

Important: These work packages establish standards and enforcement infrastructure. They do not authorize building the full menu product yet. Detailed application modules and their implementation remain governed by subsequent architecture documents.
Execution plan
WP-ARC02-01 — Architecture Governance Foundation
Objective: Establish architectural governance and decision control.
Actions
1. Create the architecture documentation directory.
2. Create the ADR directory.
3. Create an ADR template.
4. Define architecture review responsibilities.
5. Define decision statuses.
6. Create a decision register.
7. Record all existing ARC-01 architectural selections.
8. Identify assumptions that require validation.
9. Establish a process for changing approved architecture.
10. Create an architecture compliance checklist.
Deliverables
docs/
├── architecture/
├── decisions/
│   ├── ADR-TEMPLATE.md
│   └── decision-register.md
└── governance/
    ├── architecture-review-policy.md
    └── architecture-compliance-checklist.md


Test cases
Test ID	Test	Expected result
GOV-001	Create an ADR using the template	All mandatory fields present
GOV-002	Create an ADR without a decision status	Validation/review rejects it
GOV-003	Record a superseded decision	Original remains traceable
GOV-004	Change a major technology without ADR	Change fails governance review
GOV-005	Trace a technical decision to ARC-01/02	Reference is available

Completion criteria
- Governance policy documented.
- ADR template approved.
- Decision register initialized.
- Existing decisions traceable.
- Review process established.
WP-ARC02-02 — Repository and Code Structure Standards
Objective: Establish the repository structure and enforceable coding conventions.
Actions
1. Inspect the existing repository state before modifying it.
2. Confirm the root directory structure.
3. Establish backend directory conventions.
4. Establish frontend directory conventions.
5. Establish shared-package boundaries.
6. Define naming conventions.
7. Define Python formatting and linting.
8. Define TypeScript linting and formatting.
9. Define type-checking requirements.
10. Add a pull request template.
11. Add contribution guidelines.
12. Add a code ownership policy where multiple contributors are involved.
Suggested tooling
Area	Tool
Python linting	Ruff
Python formatting	Ruff formatter
Python typing	Pyright
TypeScript linting	ESLint
TypeScript formatting	Prettier
Frontend type checking	TypeScript compiler
Git hooks	Pre-commit, optional

Deliverables
backend/
frontend/
packages/
docs/
tests/
.github/
├── CONTRIBUTING.md
├── pull_request_template.md
└── CODEOWNERS


Test cases
Test ID	Test	Expected result
CODE-001	Run Python linting	No unapproved violations
CODE-002	Run Python formatter check	Formatting compliant
CODE-003	Run backend type checking	No blocking type errors
CODE-004	Run TypeScript type checking	No blocking type errors
CODE-005	Introduce an invalid naming convention	Review or lint catches it
CODE-006	Introduce an unauthorized import	Architecture check flags it

Completion criteria
The repository has consistent, repeatable, automated code-quality checks.
WP-ARC02-03 — Module Boundary and Dependency Standards
Objective: Prevent circular dependencies and uncontrolled module coupling.
Actions
1. Define module ownership.
2. Define allowed import directions.
3. Define public module interfaces.
4. Identify shared utilities.
5. Prohibit direct imports of private module internals.
6. Define dependency rules between layers.
7. Create dependency inspection scripts.
8. Add automated architecture checks to CI.
9. Review exceptions and document approved ones.
Proposed dependency rules
API
 |
 v
Application
 |
 v
Domain
 ^
 |
Infrastructure


A more precise implementation rule is that the domain must not depend on infrastructure. Infrastructure implements interfaces required by the application or domain. API and application layers may depend on domain contracts.
Test cases
Test ID	Test	Expected result
MOD-001	Inspect module dependencies	Dependencies match approved graph
MOD-002	Introduce circular import	CI fails
MOD-003	Import a private module implementation	CI flags violation
MOD-004	Test a module independently	Tests run without full application
MOD-005	Add a valid adapter implementation	Architecture checks pass

Completion criteria
- Module boundaries documented.
- Dependency rules automated.
- No unexplained circular dependencies.
- Exceptions recorded.
WP-ARC02-04 — API and Contract Standards
Objective: Standardize communication between the frontend, backend, and public menu renderer.
Actions
1. Define REST conventions.
2. Define API versioning.
3. Define request and response schemas.
4. Define error formats.
5. Define pagination.
6. Define authentication and authorization requirements.
7. Define idempotency rules.
8. Generate OpenAPI documentation.
9. Define compatibility checks.
10. Define public versus private endpoint classifications.
Test cases
Test ID	Test	Expected result
API-001	Invalid request payload	Consistent validation response
API-002	Unauthorized private endpoint	401 or appropriate authentication response
API-003	Authenticated but unauthorized operation	403 or documented non-disclosure response
API-004	Unknown resource	Consistent not-found response
API-005	OpenAPI generation	Valid API specification
API-006	Breaking contract change	Compatibility check detects it

Completion criteria
API conventions and contract-validation procedures are documented and testable.
WP-ARC02-05 — Database and Persistence Standards
Objective: Establish safe, consistent database development rules.
Actions
1. Define table and column naming conventions.
2. Define primary-key and foreign-key rules.
3. Define tenant ownership requirements.
4. Define indexing conventions.
5. Define migration conventions.
6. Define monetary storage rules.
7. Define timestamp conventions.
8. Define transaction boundaries.
9. Define immutable snapshot storage rules.
10. Define backup and restore procedures.
11. Define migration verification tests.
12. Define production migration approval requirements.
Test cases
Test ID	Test	Expected result
DB-001	Apply all migrations to an empty database	Successful schema creation
DB-002	Upgrade a previous schema	Data preserved
DB-003	Roll back a safe migration	Expected prior state restored
DB-004	Check tenant ownership constraints	Cross-tenant references rejected
DB-005	Store monetary values	Exact decimal/minor-unit representation
DB-006	Test snapshot immutability	Published snapshot cannot be modified
DB-007	Restore a backup	Database restored and usable

Completion criteria
A database governance standard and repeatable migration testing process exist.
WP-ARC02-06 — Security Standards and Enforcement
Objective: Establish security requirements before implementing sensitive business modules.
Actions
1. Define authentication standards.
2. Define role and permission models.
3. Define tenant authorization rules.
4. Define session and cookie policies.
5. Define input validation standards.
6. Define upload security standards.
7. Define secret-management standards.
8. Define audit-log requirements.
9. Define rate-limiting policy.
10. Define dependency scanning.
11. Define static security analysis.
12. Define tenant-isolation testing requirements.
13. Define security incident and remediation procedures.
Proposed tooling
- Bandit for Python security analysis.
- pip-audit for Python dependency vulnerabilities.
- Semgrep for static analysis.
- Dependency review for dependency changes.
- Secret scanning.
- OWASP ZAP for selected dynamic security tests.
These tools complement one another; none is a substitute for manual security review or application-specific testing.
Test cases
Test ID	Test	Expected result
SEC-001	Access protected endpoint without authentication	Rejected
SEC-002	User attempts another tenant's resource	Rejected
SEC-003	Restaurant user attempts platform administration	Rejected
SEC-004	Invalid file upload	Rejected
SEC-005	Secret introduced into tracked source	Secret scan fails
SEC-006	Known vulnerable dependency introduced	Dependency check flags it
SEC-007	Public request attempts to access draft data	Rejected
SEC-008	Unauthorized publishing request	Rejected and audited

Completion criteria
Security policies are documented, automated scans operate, and critical authorization tests are available.
WP-ARC02-07 — Configuration and Extensibility Standards
Objective: Ensure the theme engine, layout engine, and component registry can evolve safely.
Actions
1. Define configuration schema conventions.
2. Define schema versioning.
3. Define validation rules.
4. Define default values.
5. Define unknown-property handling.
6. Define configuration migrations.
7. Define component registration contracts.
8. Define safe fallback behavior.
9. Define compatibility checks.
10. Define configuration export/import rules.
Test cases
Test ID	Test	Expected result
CFG-001	Valid configuration	Accepted
CFG-002	Invalid token value	Rejected
CFG-003	Unknown component	Controlled rejection/fallback
CFG-004	Missing optional property	Documented default applied
CFG-005	Unsupported schema version	Controlled error
CFG-006	Valid schema migration	Configuration remains usable
CFG-007	Arbitrary executable configuration	Rejected

Completion criteria
Configuration contracts are versioned, validated, and compatible with controlled extensions.
WP-ARC02-08 — Testing and Quality Assurance Standards
Objective: Establish a common verification framework for all modules.
Actions
1. Define test categories.
2. Define test naming conventions.
3. Define test directory structure.
4. Define unit-test coverage expectations.
5. Define integration testing requirements.
6. Define end-to-end test requirements.
7. Define security testing requirements.
8. Define performance testing requirements.
9. Define test-data isolation.
10. Define CI quality gates.
11. Define test evidence and reporting.
12. Define defect severity and acceptance rules.
Test directory structure
tests/
├── unit/
├── integration/
├── contract/
├── security/
├── performance/
├── e2e/
├── architecture/
└── fixtures/


Test naming convention
test_<feature>_<scenario>_<expected_result>


Examples:
def test_menu_creation_with_valid_data_succeeds():    ...def test_menu_access_from_another_tenant_is_rejected():    ...def test_published_snapshot_remains_immutable():    ...



Completion criteria
Every future module has a defined test strategy and CI enforcement policy.
WP-ARC02-09 — Deployment and Operational Standards
Objective: Ensure that the managed and self-hosted editions follow the same application architecture.
Actions
1. Define environment separation.
2. Define environment-variable naming.
3. Define secrets management.
4. Define Docker image standards.
5. Define database initialization and migration behavior.
6. Define health checks.
7. Define backup schedules and retention.
8. Define restoration tests.
9. Define deployment approval rules.
10. Define rollback procedures.
11. Define observability requirements.
12. Define minimum self-hosted operational documentation.
Test cases
Test ID	Test	Expected result
DEP-001	Start services using Docker Compose	Services start successfully
DEP-002	Missing mandatory environment variable	Clear startup failure
DEP-003	Optional Redis unavailable	Core application remains operational
DEP-004	Database unavailable	Controlled failure and health reporting
DEP-005	Apply migrations during deployment	Successful migration
DEP-006	Restore database backup	Application data restored
DEP-007	Deploy with different storage adapter	Core business logic unchanged

Completion criteria
A deployment standard exists for development, staging, production, and customer-hosted environments.
WP-ARC02-10 — Architecture Compliance and Final Review
Objective: Verify that all ARC-02 requirements have been implemented as engineering controls.
Actions
1. Review every principle.
2. Review every system constraint.
3. Inspect repository structure.
4. Inspect dependency graph.
5. Review API and database standards.
6. Review security enforcement.
7. Run architecture tests.
8. Run linting and type checking.
9. Run test suites.
10. Inspect CI/CD enforcement.
11. Review documentation completeness.
12. Record unresolved risks.
13. Produce the architecture compliance report.
14. Obtain architectural approval before proceeding.
Final deliverables
docs/reports/
├── ARC-02-compliance-report.md
├── ARC-02-test-report.md
├── ARC-02-security-review.md
├── ARC-02-deviation-register.md
└── ARC-02-approval-record.md



11. Automated enforcement and CI/CD implementation
The principles above must be converted into automated checks wherever possible.
11.1 Required quality gates
Proposed CI pipeline
1. Source validation
   
   Formatting, linting, syntax and type checks.
2. Architecture validation
   
   Module boundaries, dependency graph and forbidden imports.
3. Security validation
   
   Secret scanning, static analysis and dependency auditing.
4. Automated testing
   
   Unit, integration, contract and security tests.
5. Build validation
   
   Frontend and backend build checks.
6. Deployment validation
   
   Container build, configuration checks and smoke tests.
7. Release approval
   
   Required review and approval before production deployment.

11.2 Example GitHub Actions workflow
The following is an initial template. It assumes a repository structure with backend/ and frontend/ directories and dependency lockfiles. Exact commands must be aligned with the actual repository once it is inspected.

name: Architecture and Quality Gates

on:
  pull_request:
  push:
    branches:
      - main
      - develop

permissions:
  contents: read

jobs:
  backend-quality:
    name: Backend Quality
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        working-directory: backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Lint
        working-directory: backend
        run: ruff check .

      - name: Format check
        working-directory: backend
        run: ruff format --check .

      - name: Type check
        working-directory: backend
        run: pyright

      - name: Unit tests
        working-directory: backend
        run: pytest tests/unit -q

  frontend-quality:
    name: Frontend Quality
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci

      - name: Lint
        working-directory: frontend
        run: npm run lint

      - name: Type check
        working-directory: frontend
        run: npx tsc --noEmit

      - name: Unit tests
        working-directory: frontend
        run: npm run test -- --run

      - name: Build
        working-directory: frontend
        run: npm run build

  architecture-checks:
    name: Architecture Compliance
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Check architecture documentation
        run: |
          test -f docs/architecture/ARC-01-system-overview.md
          test -f docs/architecture/ARC-02-principles-standards-constraints.md

      - name: Run architecture tests
        run: |
          python -m pip install pytest
          pytest tests/architecture -q

  dependency-security:
    name: Dependency Security
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependency auditor
        run: pip install pip-audit

      - name: Audit Python dependencies
        working-directory: backend
        run: pip-audit -r requirements.txt

  secret-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Scan repository
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}



Workflow implementation cautions:
- Pin third-party Actions to reviewed immutable commit SHAs before production adoption.
- Align Python and Node versions with the project's validated runtime matrix.
- Use locked dependency files.
- Ensure the frontend scripts actually exist before enabling the workflow.
- Add database-backed integration jobs separately.
- Add explicit pull-request branch protection so failed checks cannot be bypassed casually.
- Configure the workflow to avoid exposing secrets to untrusted pull-request code.
11.3 Architecture test examples
The following examples show how architecture rules can be tested programmatically.
from pathlib import PathBACKEND = Path("backend/app/modules")FORBIDDEN_IMPORTS = {    "app.modules.menus.internal_repository",    "app.modules.publishing.internal_service",}def test_forbidden_private_imports_are_absent():    violations = []    for source in BACKEND.rglob("*.py"):        content = source.read_text(encoding="utf-8")        for forbidden in FORBIDDEN_IMPORTS:            if forbidden in content:                violations.append(                    f"{source}: {forbidden}"                )    assert not violations, "\n".join(violations)



This is a deliberately simple starting point. A production-grade architecture checker should parse Python import syntax into an AST, distinguish actual imports from comments and strings, and evaluate imports against an approved dependency graph.
11.4 Test enforcement matrix
Standard	Automated enforcement	Human review
Formatting	Ruff, Prettier	Exception review
Type safety	Pyright, TypeScript	API design review
Module boundaries	Architecture tests	Boundary review
API compatibility	OpenAPI comparison	Contract review
Database migration	Migration tests	Migration approval
Tenant isolation	Integration tests	Security review
Snapshot immutability	Automated tests	Data-model review
Configuration validation	Schema tests	UX/architecture review
Secret exposure	Secret scanner	Incident review
Dependency health	Audit tools	License and maintenance review
Deployment portability	Container tests	Operations review


12. Comprehensive test case catalogue
The following catalogue is the acceptance baseline for ARC-02. The cases are architecture-control tests; they do not imply that the full business functionality has already been implemented.
12.1 Architectural principles tests
Test ID	Scenario	Expected result
ARC02-001	Module contains unrelated business responsibilities	Review identifies violation
ARC02-002	Circular dependency introduced	Automated check fails
ARC02-003	Business logic depends on HTTP framework	Architecture check flags violation
ARC02-004	Theme change modifies menu content records	Test fails
ARC02-005	Renderer requires dashboard state	Independence test fails
ARC02-006	Published snapshot is modified	Immutability test fails
ARC02-007	Core module requires Redis to operate	Resilience test fails
ARC02-008	Self-hosted edition requires separate business logic	Portability review fails

12.2 Security tests
Test ID	Scenario	Expected result
ARC02-SEC-001	Unauthenticated user accesses private resource	Denied
ARC02-SEC-002	Tenant A accesses Tenant B's resource	Denied
ARC02-SEC-003	Menu Editor attempts platform administration	Denied
ARC02-SEC-004	Public user accesses unpublished menu	Denied
ARC02-SEC-005	Invalid file type is uploaded	Rejected
ARC02-SEC-006	Malformed configuration is submitted	Rejected
ARC02-SEC-007	Secret is committed to source	CI fails
ARC02-SEC-008	Rate limit is exceeded	Request throttled

12.3 Data and API tests
Test ID	Scenario	Expected result
ARC02-DATA-001	Apply migration from empty database	Success
ARC02-DATA-002	Apply migration to existing data	Data preserved
ARC02-DATA-003	Invalid foreign-key relationship	Rejected
ARC02-DATA-004	Invalid tenant relationship	Rejected
ARC02-DATA-005	Currency precision calculation	Exact result
ARC02-API-001	Invalid request schema	Standard error
ARC02-API-002	Invalid pagination values	Validation error
ARC02-API-003	Unauthorized API operation	Denied
ARC02-API-004	API schema changes incompatibly	Compatibility check fails

12.4 Configuration and renderer tests
Test ID	Scenario	Expected result
ARC02-UI-001	Switch theme preset	Content unchanged
ARC02-UI-002	Switch layout	Menu data unchanged
ARC02-UI-003	Disable a component	Component hidden
ARC02-UI-004	Unsupported component type	Controlled fallback/error
ARC02-UI-005	Invalid token	Rejected
ARC02-UI-006	Render at mobile viewport	No critical overflow
ARC02-UI-007	Renderer runs without dashboard	Successful rendering
ARC02-UI-008	Missing optional image	Graceful fallback

12.5 Operational tests
Test ID	Scenario	Expected result
ARC02-OPS-001	Start with valid environment	Services start
ARC02-OPS-002	Missing required environment variable	Clear failure
ARC02-OPS-003	Database becomes unavailable	Controlled degraded state
ARC02-OPS-004	Redis unavailable	Core features remain available
ARC02-OPS-005	Restore backup	Valid application state
ARC02-OPS-006	Deploy self-hosted edition	Successful startup
ARC02-OPS-007	Roll back application release	Documented recovery succeeds


13. Verification and validation strategy
Verification and validation are separate activities and must have separate evidence.
13.1 Verification — Are we building the system according to the architecture?
Verification checks whether engineering work complies with ARC-02.

Methods:
- Source code inspection.
- Architecture dependency analysis.
- Automated linting.
- Type checking.
- Schema validation.
- Migration testing.
- Unit testing.
- Integration testing.
- Security testing.
- CI/CD pipeline inspection.
- Documentation review.
Example:

Requirement: Published snapshots must be immutable.

Verification activities:
1. Inspect snapshot persistence design.
2. Inspect database constraints and permissions.
3. Inspect publishing service behavior.
4. Attempt to modify a published snapshot.
5. Execute historical version comparison.
6. Confirm the test fails when immutability is deliberately broken.
Expected evidence: automated test results, implementation review, and database-level verification where applicable.
13.2 Validation — Does the architecture meet the actual product needs?
Validation determines whether the selected architecture is appropriate for the intended product.

Methods:
- Architecture scenario testing.
- Prototype evaluation.
- Deployment portability demonstration.
- Multi-tenant isolation demonstration.
- Theme and layout flexibility demonstration.
- Public renderer independence demonstration.
- Operational recovery demonstration.
- Stakeholder review.
Example:

Requirement: Restaurants must customize the visual experience without requiring source code changes.

Validation activities:
1. Create a representative restaurant.
2. Create a menu.
3. Select a theme.
4. Change colors and typography.
5. Change layout.
6. Enable and disable supported components.
7. Preview the menu.
8. Publish the configuration.
9. Open the public menu from a separate browser.
10. Confirm the changes are reflected.
Expected evidence: a complete end-to-end demonstration and recorded acceptance result.
13.3 V&V traceability matrix
Requirement	Verification	Validation
Modularity	Dependency tests	Independent module development
Tenant isolation	Security integration tests	Tenant A/B isolation demonstration
Theme customization	Configuration tests	Restaurant customization demonstration
Renderer independence	Architecture tests	Standalone public rendering
Immutable snapshots	Database and service tests	Historical publication and rollback demonstration
Portability	Container tests	Managed and self-hosted deployment
Security	Automated security tests	Threat-scenario assessment
Reliability	Failure and recovery tests	Operational recovery demonstration
Extensibility	Contract and compatibility tests	Add new component/theme without core rewrite

13.4 Evidence requirements
Every completed test must produce:
- Test identifier.
- Requirement identifier.
- Test description.
- Test environment.
- Preconditions.
- Execution steps.
- Actual result.
- Expected result.
- Pass/fail status.
- Evidence location.
- Tester or reviewer.
- Execution date.
- Defect reference, if applicable.
A test must not be marked passed simply because the relevant code exists.

14. Non-functional acceptance targets
These targets provide an initial quality direction. They are not yet verified production guarantees and must be validated through later performance and operational architecture work.
Attribute	Proposed initial target	Validation method
Responsive UI	Usable from 360px width	Browser testing
Accessibility	WCAG 2.2 AA target	Automated and manual audit
Largest Contentful Paint	Under 2.5 seconds	Field/lab performance testing
Cumulative Layout Shift	Under 0.1	Performance testing
Interaction to Next Paint	Under 200ms	Field/lab performance testing
Ordinary API latency	p95 under 500ms, uncached	Load testing
Availability	Defined SLO before production	Monitoring
Data integrity	No silent publication corruption	Consistency tests
Tenant isolation	No unauthorized cross-tenant access	Security testing
Deployment portability	Common core in both editions	Deployment demonstration

Performance results must state the tested hardware, dataset, traffic profile, network conditions, and test duration.

15. Risk register and mitigation
Risk ID	Risk	Impact	Mitigation
R-ARC02-01	Standards become too restrictive	Slower development	Allow documented exceptions
R-ARC02-02	Standards remain documentation-only	Architecture drift	CI enforcement
R-ARC02-03	Overengineering before MVP	Increased cost and delay	Apply minimum necessary controls
R-ARC02-04	Uncontrolled module dependencies	Difficult maintenance	Dependency graph and review
R-ARC02-05	Incomplete tenant isolation	Data exposure	Defense-in-depth testing
R-ARC02-06	Configuration schema incompatibility	Broken menus	Schema versioning and migration
R-ARC02-07	Incomplete migration strategy	Data loss	Backup and migration verification
R-ARC02-08	Deployment-specific business logic	Forked editions	Shared core and adapters
R-ARC02-09	Unreviewed dependencies	Security and licensing risks	Dependency approval policy
R-ARC02-10	Incomplete test evidence	False confidence	Traceable V&V records


16. ARC-02 completion and approval criteria
ARC-02 should not be considered complete merely because its documentation has been written.

It must pass the following completion requirements.
ARC-02 completion tracker
15/15 complete

[x] GOV-01 Architecture governance policy documented
[x] GOV-02 ADR template and decision register created
[x] CODE-01 Backend and frontend coding standards defined
[x] CODE-02 Repository structure and naming standards defined
[x] ARCH-01 Module boundaries and dependency rules defined
[x] API-01 API standards and error contracts documented
[x] DB-01 Database and migration standards documented
[x] SEC-01 Security standards and enforcement requirements documented
[x] CFG-01 Configuration and extensibility standards defined
[x] TEST-01 Testing standards and test catalogue established
[x] CI-01 Automated quality gates implemented
[x] DEP-01 Deployment and operational standards documented
[x] VV-01 Verification and validation matrix established
[x] REP-01 Architecture compliance report produced
[x] APR-01 Architecture review and approval recorded

Reset checklist
Planning checklist only. Checking an item here does not independently verify that the corresponding work has been completed.
Approval conditions
ARC-02 can be approved when:
1. All mandatory principles are defined.
2. Constraints are unambiguous.
3. Coding and documentation standards are established.
4. Security and tenant-isolation requirements are explicit.
5. Test cases have traceable requirement identifiers.
6. CI enforcement has been implemented and demonstrated.
7. Unresolved architectural decisions are recorded.
8. Known deviations have documented justifications.
9. Verification and validation responsibilities are assigned.
10. The architecture reviewer approves the baseline.

17. Decisions requiring explicit review
The following areas should not be treated as permanently settled merely because they appear in this document.
Decision	Current proposal	Review requirement
Python runtime	Python 3.12 baseline in CI example	Confirm supported runtime and local development compatibility
Node runtime	Node 22 baseline in CI example	Confirm deployment compatibility
Tenant isolation	Shared database/schema + RLS	Validate transaction and connection-pooling behavior
Authentication	Secure session-based authentication	Define session lifecycle and recovery
Component extensibility	Allowlisted registry	Define component compatibility and migration policy
Configuration storage	Versioned JSONB configurations	Define schema validation and migration
Public menu delivery	Published snapshots	Define caching and invalidation guarantees
Self-hosted licensing	Signed deployment entitlements	Define offline grace period and recovery
Accessibility	WCAG 2.2 AA target	Confirm test strategy and scope
Performance	Initial targets in Section 14	Validate against realistic restaurant traffic

These decisions should be finalized through subsequent architecture documents and ADRs.

18. Final ARC-02 outcome
ARC-02 establishes the engineering governance foundation for ModularMenu.

It defines how the system must be built, what implementations are prohibited, how code quality is enforced, how architectural decisions are controlled, and how compliance is verified.

Its most important outcome is a common engineering contract across the entire platform:
- One modular core.
- Strict tenant isolation.
- Independent content and presentation.
- Configuration-driven customization.
- A reusable and controlled component ecosystem.
- Independent public menu rendering.
- Immutable published versions.
- Provider-independent business logic.
- Consistent coding and API standards.
- Automated architecture and security checks.
- Traceable testing and validation evidence.
ARC-02 must be treated as the engineering baseline for all subsequent architecture documents. If a future module requires a deviation, that deviation must be justified and documented rather than introduced silently.

19. Next architecture document
Next in sequence
ARC-03 — Application Architecture
Purpose: Define the actual application structure, application layers, frontend/backend responsibilities, request lifecycle, service boundaries, application orchestration, and communication patterns.

Proposed coverage:
1. Application architecture overview.
2. Frontend application architecture.
3. Backend application architecture.
4. Application-layer responsibilities.
5. Request and response lifecycle.
6. Service and repository patterns.
7. Shared package architecture.
8. Frontend/backend communication.
9. Application configuration and environment handling.
10. Application-level testing, verification and validation.

Recommended execution order: Complete the ARC-02 documentation and review first; implement its governance and quality-enforcement foundation as a controlled work package; then proceed to ARC-03. Do not begin full product-module implementation until the architecture sequence has established the required contracts.
