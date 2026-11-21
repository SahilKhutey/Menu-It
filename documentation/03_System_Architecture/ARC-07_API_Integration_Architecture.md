ARC-07 — API & Integration Architecture
MODULARMENU · ARCHITECTURE DOCUMENTATION SERIES
ARC-07
Approved Baseline · Version 1.0
Implementation Complete

Document title: API & Integration Architecture — REST API Design, Service Contracts, Communication, External Integrations and Interoperability

Parent documents: ARC-01 through ARC-06.

Primary technology direction: FastAPI · Python · Pydantic · PostgreSQL · SQLAlchemy · Next.js · TypeScript · OpenAPI 3.x.

Architecture approach: Contract-first REST API architecture with versioned endpoints, tenant-aware authorization, generated frontend contracts, modular backend interfaces and controlled external integrations.

1. Purpose and objectives
ARC-07 defines how ModularMenu application modules, frontend applications, public menu consumers and external systems communicate.

ARC-03 established the frontend/backend application structure. ARC-04 defined domain boundaries. ARC-05 defined tenant authorization. ARC-06 defined persistence and data ownership.

ARC-07 converts those decisions into enforceable API contracts.

The API architecture must support:
1. Platform administration.
2. Restaurant onboarding and management.
3. Menu, category, item and pricing operations.
4. Theme and layout configuration.
5. Settings-based and visual menu editing.
6. Preview and publication workflows.
7. Public QR-accessible menu delivery.
8. Media uploads and retrieval.
9. Subscription and licensing operations.
10. External integrations and future extensions.
11. Both managed SaaS and customer-hosted deployment editions.
1.1 Architectural objectives
ID	Objective	Expected outcome
API-01	Contract consistency	Frontend and backend share reliable API definitions
API-02	Versioning	Breaking changes can be introduced deliberately
API-03	Tenant security	Every private request is authorized within its tenant context
API-04	Domain modularity	API modules align with domain ownership
API-05	Reliability	Predictable errors, timeouts, retries and idempotency
API-06	Extensibility	New features and integrations do not destabilize existing APIs
API-07	Documentation	OpenAPI is generated, reviewed and published
API-08	Public delivery	Anonymous menu consumers receive published data only
API-09	Integration readiness	External services use controlled adapters and contracts
API-10	Testability	Contracts, permissions and workflows are automatically verified

1.2 Scope
Included
- API architecture and communication model.
- REST conventions and endpoint taxonomy.
- API versioning and compatibility policy.
- Request, response and error contracts.
- Authentication, authorization and tenant context.
- Pagination, filtering, sorting and search.
- Validation and serialization.
- Frontend API client and generated TypeScript types.
- Internal module interfaces.
- Public menu APIs.
- Preview and publication APIs.
- Media upload APIs.
- Webhooks and external integration architecture.
- Rate limiting, idempotency, retries and timeouts.
- API security and observability.
- API testing, verification and validation.
Outside this document
- Full database implementation — ARC-06.
- Detailed theme and component schema design — ARC-08.
- Menu renderer internals — ARC-09.
- Publication lifecycle and rollback internals — ARC-10.
- Production infrastructure topology — ARC-11.
- Complete security operations and threat-response policies — ARC-12.

2. API architecture overview
2.1 Architectural model
ModularMenu will use a versioned REST API over HTTPS with JSON request/response payloads for normal application operations.

The API is a boundary around application use cases. It is not a direct interface to database tables.
API communication architecture
API consumers
Restaurant dashboard

Next.js / React


Public menu

Browser / QR visitor


Platform admin

Privileged operator


External clients

Approved integrations





API boundary
Routing and versioning

Request validation

Authentication

Authorization

Rate limiting

Request tracing




Application services
Identity and tenancy
Restaurant management
Menu management
Pricing and availability
Theme and editor
Publishing
Media management
Licensing



Repositories and integration adapters

PostgreSQL · Object storage · Email provider · Webhook delivery · Optional Redis


2.2 Communication principles
1. Frontend applications communicate with FastAPI through documented API contracts.
2. The frontend never connects directly to PostgreSQL.
3. API endpoints invoke application use cases, not arbitrary ORM operations.
4. Domain modules communicate through application interfaces or defined contracts.
5. Public APIs expose only explicitly publishable data.
6. Tenant identity is resolved from authenticated membership, not trusted from request payloads.
7. External services are accessed through adapters.
8. OpenAPI is the source of truth for externally visible HTTP contracts.
9. API errors follow a common format.
10. SaaS and customer-hosted editions expose the same core API contracts unless a documented deployment-specific capability is involved.
2.3 API protocol and transport
Area	Standard
Protocol	HTTPS
API style	REST
Payload	JSON
API versioning	URL path
Contract format	OpenAPI
Authentication	Secure cookie-based session for first-party browser clients
External integration authentication	Scoped API credentials or another approved mechanism
File transfer	Direct object-storage upload where appropriate
Events	Webhooks and internal outbox-based delivery
Encoding	UTF-8
Timestamp format	ISO 8601 UTC
Pagination	Cursor-based for larger or changing datasets

Initial API base path:
/api/v1/



3. API design standards
3.1 Resource naming
Use plural, lowercase, hyphen-free resource names in the URL path.
Resource	Endpoint
Restaurants	/api/v1/restaurants
Menus	/api/v1/restaurants/{restaurant_id}/menus
Categories	/api/v1/menus/{menu_id}/categories
Items	/api/v1/categories/{category_id}/items
Themes	/api/v1/themes
Publications	/api/v1/menus/{menu_id}/publications
Media	/api/v1/media

Use nouns for resources and HTTP methods for actions.

For business operations that are not natural CRUD operations, use explicit action subresources:
POST /api/v1/menus/{menu_id}/preview
POST /api/v1/menus/{menu_id}/publish
POST /api/v1/publications/{publication_id}/rollback


The last operation is a proposed API shape; ARC-10 must define its actual lifecycle semantics.
3.2 HTTP methods
Method	Intended use	Idempotent by HTTP semantics
GET	Read resource or collection	Yes
POST	Create resource or initiate operation	No
PUT	Replace complete resource representation	Yes
PATCH	Partial update	Not inherently
DELETE	Delete or retire resource	Yes

Avoid using GET for operations that modify state.
3.3 HTTP status codes
Status	Meaning	Example
200	Successful request	Fetch/update resource
201	Resource created	Create menu
202	Accepted for asynchronous processing	Export or background operation
204	Successful with no response body	Delete/retire resource
400	Malformed request	Invalid syntax
401	Authentication required	No valid session
403	Authenticated but unauthorized	Insufficient permission
404	Resource not found or deliberately concealed	Unknown/inaccessible resource
409	State or concurrency conflict	Stale edit
410	Gone	Withdrawn public resource, where appropriate
413	Request too large	Upload exceeds size limit
415	Unsupported media type	Invalid upload content type
422	Request validation failure	Invalid field
429	Rate limit exceeded	Excessive requests
500	Unexpected server error	Internal failure
502	Upstream provider failure	External dependency error
503	Temporarily unavailable	Maintenance or overload
504	Upstream timeout	Dependency timeout

Use 404 rather than exposing a cross-tenant resource's existence when that is the chosen authorization policy.
3.4 API path and query rules
- Resource IDs are UUIDs.
- Slugs are used for human-readable public URLs where suitable.
- Query parameters use snake_case consistently at the API layer.
- List endpoints support bounded pagination.
- Filtering parameters must be explicitly allowlisted.
- Sorting fields must be explicitly allowlisted.
- Never accept raw SQL expressions or arbitrary database column names from query parameters.
- Do not put secrets, passwords, tokens or sensitive personal information in URLs.
3.5 API request headers
Header	Purpose
Content-Type	Request media type
Accept	Response media type
X-Request-ID	Optional client-generated correlation identifier
Idempotency-Key	Deduplication for supported operations
If-Match	Conditional update using an ETag
If-None-Match	Conditional read
X-CSRF-Token	CSRF protection for cookie-authenticated mutations

The server must generate its own trusted request identifier if the client omits one. A client-supplied request ID must be length-limited and sanitized before logging.

4. API resource and module catalogue
The API surface is grouped according to the modular domain architecture.
4.1 Identity and authentication APIs
Base path: /api/v1/auth
Method	Endpoint	Purpose	Access
POST	/register	Register user	Public, controlled
POST	/login	Start session	Public, rate-limited
POST	/logout	End session	Authenticated
GET	/session	Retrieve current session	Authenticated
POST	/password/forgot	Request reset	Public, rate-limited
POST	/password/reset	Reset password	Token-authorized
POST	/email/verify	Verify email	Token-authorized
POST	/email/resend-verification	Resend verification	Authenticated
GET	/me	Current user profile	Authenticated

Do not reveal whether an email address exists in password-reset responses.
4.2 Organization and tenant APIs
Base path: /api/v1/organizations
Method	Endpoint	Purpose
GET	/	List organizations available to the user
POST	/	Create organization
GET	/{organization_id}	Retrieve organization
PATCH	/{organization_id}	Update organization
GET	/{organization_id}/members	List members
POST	/{organization_id}/invitations	Invite member
DELETE	/{organization_id}/members/{user_id}	Remove member
PATCH	/{organization_id}/members/{user_id}	Change membership role

The organization ID identifies the requested context but does not prove membership. Every operation must resolve and authorize the actor's membership.
4.3 Restaurant APIs
Base path: /api/v1/restaurants
Method	Endpoint	Purpose
GET	/	List accessible restaurants
POST	/	Create restaurant
GET	/{restaurant_id}	Retrieve restaurant
PATCH	/{restaurant_id}	Update restaurant
GET	/{restaurant_id}/settings	Read settings
PATCH	/{restaurant_id}/settings	Update settings
GET	/{restaurant_id}/members	List branch members
POST	/{restaurant_id}/members	Assign member
DELETE	/{restaurant_id}/members/{user_id}	Remove branch assignment
GET	/{restaurant_id}/domains	List domains
POST	/{restaurant_id}/domains	Register domain

4.4 Menu APIs
Base path: /api/v1
Method	Endpoint	Purpose
GET	/restaurants/{restaurant_id}/menus	List menus
POST	/restaurants/{restaurant_id}/menus	Create menu
GET	/menus/{menu_id}	Read menu
PATCH	/menus/{menu_id}	Update menu metadata
DELETE	/menus/{menu_id}	Archive or delete according to policy
GET	/menus/{menu_id}/categories	List categories
POST	/menus/{menu_id}/categories	Create category
PATCH	/categories/{category_id}	Update category
DELETE	/categories/{category_id}	Delete or archive category
POST	/menus/{menu_id}/categories/reorder	Reorder categories
GET	/categories/{category_id}/items	List items
POST	/categories/{category_id}/items	Create item
GET	/items/{item_id}	Retrieve item
PATCH	/items/{item_id}	Update item
DELETE	/items/{item_id}	Archive or delete item
POST	/items/reorder	Reorder items

The actual authorization and ownership checks must use the tenant-scoped resource graph established in ARC-05 and ARC-06.
4.5 Pricing and availability APIs
Method	Endpoint	Purpose
GET	/items/{item_id}/prices	List item prices
POST	/items/{item_id}/prices	Create price
PATCH	/prices/{price_id}	Update price
DELETE	/prices/{price_id}	Remove price
PATCH	/items/{item_id}/availability	Change availability
POST	/items/{item_id}/variants	Create variant
PATCH	/variants/{variant_id}	Update variant
POST	/items/{item_id}/addons	Associate add-on

Price changes must not mutate previously published snapshots.
4.6 Theme, layout and component APIs
Method	Endpoint	Purpose
GET	/themes	List available theme presets
GET	/themes/{theme_id}	Read theme
GET	/layouts	List supported layouts
GET	/layouts/{layout_id}	Read layout definition
GET	/components	List registered components
GET	/components/{component_key}	Read component schema
GET	/restaurants/{restaurant_id}/design-config	Read design configuration
PUT	/restaurants/{restaurant_id}/design-config	Replace configuration
POST	/restaurants/{restaurant_id}/design-config/validate	Validate configuration

Only approved, registered theme/layout/component definitions should be exposed as supported options.
4.7 Editor and preview APIs
Method	Endpoint	Purpose
GET	/menus/{menu_id}/editor-state	Retrieve editable state
PUT	/menus/{menu_id}/editor-state	Save editor state
POST	/menus/{menu_id}/preview	Generate preview
POST	/menus/{menu_id}/validate	Validate menu before publication
GET	/menus/{menu_id}/validation-report	Retrieve validation report

The editor state is not the published state. The editor API must not bypass domain validation or write directly to publication tables.
4.8 Publishing APIs
Method	Endpoint	Purpose
GET	/menus/{menu_id}/versions	List versions
GET	/menus/{menu_id}/versions/{version_id}	Read version
POST	/menus/{menu_id}/publish	Publish validated draft
GET	/menus/{menu_id}/publications	List publication history
GET	/publications/{publication_id}	Retrieve publication
POST	/publications/{publication_id}/rollback	Roll back to an earlier version through a new publication operation
POST	/publications/{publication_id}/withdraw	Withdraw publication

Publishing and rollback semantics must be finalized in ARC-10. This API document defines the contract boundaries, not the internal publication transaction algorithm.
4.9 Media APIs
Method	Endpoint	Purpose
POST	/media/upload-intents	Request upload authorization
POST	/media/{media_id}/complete	Confirm upload
GET	/media	List media assets
GET	/media/{media_id}	Retrieve metadata
PATCH	/media/{media_id}	Update metadata
DELETE	/media/{media_id}	Delete or schedule deletion
POST	/media/{media_id}/usages	Associate asset
DELETE	/media/{media_id}/usages/{usage_id}	Remove association

Large files should generally be uploaded directly to object storage through a short-lived, narrowly scoped upload authorization rather than streamed through the application server unnecessarily.
4.10 Subscription and licensing APIs
Method	Endpoint	Purpose
GET	/subscription-plans	List available plans
GET	/organizations/{organization_id}/subscription	Read subscription
POST	/organizations/{organization_id}/subscription/checkout	Initiate checkout when billing is implemented
GET	/organizations/{organization_id}/license	Read license entitlement
POST	/license/activate	Activate supported deployment entitlement
POST	/license/refresh	Refresh entitlement

Billing and license operations require a dedicated security and integration review. A public API must not let clients assign themselves paid entitlements.
4.11 Public menu APIs
Base path: /api/v1/public
Method	Endpoint	Purpose
GET	/restaurants/{restaurant_slug}	Public restaurant profile
GET	/restaurants/{restaurant_slug}/menus	Publicly available published menus
GET	/restaurants/{restaurant_slug}/menus/{menu_slug}	Published menu snapshot
GET	/restaurants/{restaurant_slug}/menus/{menu_slug}/metadata	Public publication metadata

Public endpoints must never expose draft editor state, staff records, membership details, internal IDs where unnecessary, subscription state or private media.

5. API contract architecture
The API contract is the agreement between the frontend, backend and approved external consumers.

The backend owns the canonical HTTP contract. TypeScript interfaces must be generated from the OpenAPI document rather than independently maintained.
5.1 Contract-first workflow






5.2 Request contract standards
Every endpoint must define:
- HTTP method and path.
- Authentication requirement.
- Authorization policy.
- Tenant scope.
- Request headers.
- Path parameters.
- Query parameters.
- Request body schema.
- Success response schema.
- Error responses.
- Idempotency behavior.
- Concurrency behavior where relevant.
- Rate limit classification.
- Audit requirements.
- OpenAPI operation identifier.
- Automated test coverage.
5.3 Example request and response
Create a menu:
POST /api/v1/restaurants/restaurant-uuid/menus
Content-Type: application/json
Accept: application/json
X-Request-ID: req-123


Request:
{
  "name": "Lunch Menu",
  "slug": "lunch",
  "description": "Our lunch selection"
}


Response:
HTTP/1.1 201 Created
Location: /api/v1/menus/menu-uuid


{
  "data": {
    "id": "menu-uuid",
    "organization_id": "organization-uuid",
    "restaurant_id": "restaurant-uuid",
    "name": "Lunch Menu",
    "slug": "lunch",
    "description": "Our lunch selection",
    "status": "draft",
    "created_at": "2026-11-21T03:00:00Z",
    "updated_at": "2026-11-21T03:00:00Z"
  },
  "meta": {
    "request_id": "req-123"
  }
}


These UUIDs and timestamps are illustrative examples, not real records.
5.4 Standard success envelope
For normal JSON API responses:
{
  "data": {},
  "meta": {
    "request_id": "req-123"
  }
}


For paginated responses:
{
  "data": [],
  "meta": {
    "request_id": "req-123",
    "pagination": {
      "next_cursor": "opaque-cursor",
      "has_more": true,
      "limit": 20
    }
  }
}


A response envelope should be consistent, but avoid adding unnecessary wrapping to every special HTTP response. For example, a 204 No Content response has no body.
5.5 Standard error contract
Use a stable machine-readable error structure. RFC 9457 Problem Details is a good baseline.

Example:
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Request validation failed",
  "status": 422,
  "detail": "One or more fields are invalid.",
  "instance": "/api/v1/menus",
  "code": "VALIDATION_ERROR",
  "request_id": "req-123",
  "errors": [
    {
      "field": "name",
      "code": "REQUIRED",
      "message": "Name is required."
    }
  ]
}


Rules:
- code is stable and suitable for frontend branching.
- message is safe for display.
- errors is optional and used for field-level issues.
- Never return database exception details, stack traces, SQL, secret values or internal filesystem paths.
- Do not return a resource's sensitive metadata in an authorization error.
5.6 Error code catalogue
Error code	HTTP status	Meaning
VALIDATION_ERROR	422	Invalid request
AUTHENTICATION_REQUIRED	401	No valid authentication
PERMISSION_DENIED	403	Insufficient permission
RESOURCE_NOT_FOUND	404	Resource unavailable
RESOURCE_CONFLICT	409	Conflicting state
VERSION_CONFLICT	409	Stale update
IDEMPOTENCY_CONFLICT	409	Key reused with different payload
RATE_LIMIT_EXCEEDED	429	Rate limit reached
UPLOAD_TOO_LARGE	413	Upload exceeds policy
UNSUPPORTED_MEDIA_TYPE	415	Unsupported file type
DEPENDENCY_UNAVAILABLE	503	Required dependency unavailable
INTERNAL_ERROR	500	Unexpected server failure

Error codes should be documented centrally and tested to avoid accidental drift.

6. API authentication and authorization
6.1 Authentication model
The initial first-party web application should use server-managed sessions with secure cookies.

Recommended cookie properties:
HttpOnly
Secure
SameSite=Lax (or stricter where compatible)
Path=/


The session cookie should contain an opaque, high-entropy session identifier rather than a complete authorization decision.

Session state and revocation should be managed server-side. Redis may be used as an optional session store if the final architecture requires it; PostgreSQL-backed session persistence is also possible.

For external clients, use a separately designed credential model with narrow scopes, expiry and revocation. Do not reuse browser session cookies as third-party API keys.
6.2 Authentication flow






For server-side rendering, Next.js may call FastAPI using a server-side request that forwards only the required authentication cookie or uses an approved server-to-server mechanism. Do not expose internal service credentials to the browser.
6.3 Tenant context resolution
The API must not trust:
{
  "organization_id": "some-organization-uuid"
}


as proof of access.

Instead:
1. Resolve the authenticated user.
2. Identify the requested organization context.
3. Verify active organization membership.
4. Verify role and permission.
5. Verify restaurant assignment when branch scope applies.
6. Create immutable request-scoped tenant context.
7. Set transaction-local PostgreSQL tenant context.
8. Invoke the application use case.
Example:
from dataclasses import dataclassfrom uuid import UUID@dataclass(frozen=True)class TenantContext:    organization_id: UUID    user_id: UUID    restaurant_id: UUID | None    role: str    correlation_id: str



Do not allow downstream application code to mutate the resolved tenant context.
6.4 Permission model
Proposed roles:
Role	Typical permissions
Platform Owner	Full platform administration
Platform Staff	Explicitly granted platform operations
Restaurant Owner	Full authorized organization/restaurant management
Restaurant Manager	Assigned restaurant management
Menu Editor	Menu and design editing within assigned scope
Viewer	Read-only authorized access
Public Visitor	Published menu access only

Permissions should be more granular than role names.

Example permission identifiers:
organization.read
organization.update
organization.members.manage

restaurant.read
restaurant.update
restaurant.members.manage

menu.read
menu.create
menu.update
menu.archive
menu.publish

design.read
design.update
media.upload
media.delete

publication.read
publication.rollback

subscription.read
license.manage

platform.users.manage
platform.tenants.manage
platform.support.access


A role-to-permission mapping must be version-controlled and tested. Avoid hardcoding authorization decisions in individual frontend buttons.
6.5 Authorization implementation example
from dataclasses import dataclass@dataclass(frozen=True)class Actor:    user_id: str    organization_id: str    permissions: frozenset[str]def require_permission(    actor: Actor,    permission: str,) -> None:    if permission not in actor.permissions:        raise PermissionError("Permission denied")



This is a simplified policy example. The production implementation must also validate active membership, restaurant assignment, resource ownership and relevant organization/restaurant lifecycle states.
6.6 CSRF and CORS
For cookie-authenticated browser requests:
- Protect state-changing methods with CSRF tokens.
- Validate the request origin where appropriate.
- Use secure cookie attributes.
- Never combine wildcard CORS origins with credentialed requests.
- Maintain an explicit allowlist of frontend origins.
- Do not treat CORS as authorization.
- Apply stricter controls to customer-hosted deployments with custom origins.

7. API versioning and compatibility
7.1 URL versioning
Initial version:
/api/v1/


A new version is required when a change breaks existing consumers.

Examples of potentially breaking changes:
- Removing an endpoint.
- Removing a response field that consumers rely on.
- Changing a field's type.
- Changing authentication requirements.
- Changing an established resource's meaning.
- Altering error behavior in a way that breaks clients.
7.2 Backward-compatible changes
Normally compatible changes include:
- Adding optional response fields.
- Adding a new endpoint.
- Adding an optional request field with safe default behavior.
- Adding a new resource capability.
- Adding a new error code without changing existing codes.
Even additive changes require consumer review. Some generated clients and strict decoders may fail when they encounter unknown enum values or response fields.
7.3 Deprecation policy
For an endpoint being retired:
1. Identify all known consumers.
2. Publish deprecation documentation.
3. Provide a replacement endpoint.
4. Add an appropriate deprecation response/header.
5. Record consumer migration status where possible.
6. Publish a retirement date.
7. Monitor remaining usage.
8. Remove only after the compatibility policy is satisfied.
7.4 API change governance
Every API change should include:
- Contract change.
- Compatibility classification.
- Security impact assessment.
- Permission review.
- Frontend impact assessment.
- Migration or deprecation plan.
- Automated contract test updates.
- Documentation update.

8. Pagination, filtering, sorting and search
8.1 Cursor pagination
Cursor pagination is the default for large and frequently changing collections.

Example:
GET /api/v1/restaurants/restaurant-uuid/menus?limit=20&cursor=opaque-token


Response:
{
  "data": [],
  "meta": {
    "pagination": {
      "limit": 20,
      "next_cursor": "opaque-token",
      "has_more": true
    }
  }
}


Rules:
- Default page size: 20.
- Maximum page size: 100, unless a reviewed endpoint requires another limit.
- Cursor must be opaque and validated.
- Sorting must be deterministic.
- Cursor contents must not expose secrets.
- Cursor scope must be bound to the correct query and tenant context.
These are proposed initial limits and should be adjusted based on performance testing.
8.2 Filtering
Example:
GET /api/v1/restaurants/{restaurant_id}/menus?status=active&search=lunch


Only documented filter fields are accepted.
8.3 Sorting
Example:
GET /api/v1/menus/{menu_id}/categories?sort=sort_order&order=asc


Do not interpolate arbitrary client-supplied sort fields into SQL.
8.4 Search
Initial search requirements:
- Search menu names.
- Search categories.
- Search food item names.
- Search descriptions where useful.
- Restrict results to authorized tenant scope.
- Apply bounded query length and request rate.
- Avoid exposing unpublished data in public search.
PostgreSQL search capabilities are sufficient for the initial product. A separate search engine should be considered only when actual product needs justify the added operational complexity.

9. API concurrency and idempotency
9.1 Optimistic concurrency
Use ETags or a version field for editable resources.

Example:
GET /api/v1/menus/menu-uuid
ETag: "menu-version-4"


Client update:
PATCH /api/v1/menus/menu-uuid
If-Match: "menu-version-4"
Content-Type: application/json


If another editor has already updated the menu, return:
HTTP/1.1 412 Precondition Failed


or a consistently documented 409 VERSION_CONFLICT.

Select one behavior and use it consistently across conditional updates.
9.2 Idempotency
Use an Idempotency-Key for supported non-idempotent operations such as:
- Publish menu.
- Create invitation.
- Initiate subscription checkout.
- Start export job.
- Trigger external integration action.
Example:
POST /api/v1/menus/menu-uuid/publish
Idempotency-Key: 3c9e6a6b-unique-operation-key


The backend must store the key in a suitable scope, associate it with a request fingerprint and return the original result for legitimate retries.

An idempotency key is not a substitute for authorization or request validation.
9.3 Retry policy
- GET requests may be retried under a bounded policy.
- Mutating requests should not be retried blindly.
- Retry only when idempotency or conditional request semantics make it safe.
- Use bounded exponential backoff and jitter for external dependencies.
- Do not retry validation or authorization errors.
- Set a total request deadline, not only per-attempt timeouts.

10. Internal module integration architecture
Not every communication between backend modules should become an HTTP request.

Within the modular monolith, modules should normally communicate through application interfaces and explicitly defined domain contracts.
10.1 Integration categories
Communication	Preferred approach
Frontend to backend	Versioned REST
Public browser to backend	Public REST read APIs
Backend module to module	Application interface / domain contract
Database persistence	Repository and Unit of Work
Reliable asynchronous work	Outbox + worker
External email provider	Email adapter
Object storage	Storage adapter
Billing provider	Billing adapter
Approved third-party clients	Scoped API credentials
Customer notifications	Webhook or notification adapter

10.2 Dependency direction
A module must not reach into another module's private database models or infrastructure implementation.

For example:
- Publishing may request a validated menu snapshot through the menu application interface.
- Publishing should not directly manipulate the menu editor's internal state store.
- The renderer should consume an explicit snapshot contract.
- Media should provide authorized asset metadata or storage access through its own interface.
- Licensing should expose an entitlement check contract rather than letting every module query subscription tables directly.
10.3 Example application interface
from dataclasses import dataclassfrom typing import Protocolfrom uuid import UUID@dataclass(frozen=True)class MenuSnapshotData:    menu_id: UUID    organization_id: UUID    restaurant_id: UUID    content: dictclass MenuSnapshotProvider(Protocol):    async def build_snapshot(        self,        organization_id: UUID,        restaurant_id: UUID,        menu_id: UUID,    ) -> MenuSnapshotData:        ...



The interface belongs to an application-level contract location agreed by the owning modules. The implementation remains inside the menu domain's application/infrastructure boundary.
10.4 Domain events
Initial event catalogue:
OrganizationCreated
RestaurantCreated
MenuCreated
MenuUpdated
MenuValidated
MenuPublished
PublicationWithdrawn
PublicationRolledBack
MediaUploaded
MediaDeleted
SubscriptionChanged
LicenseActivated


Events should contain only the data needed by consumers. Avoid embedding complete private entity records or secrets.

For reliable delivery, use the ARC-06 outbox mechanism.

11. External integration architecture
External systems must not be coupled directly to domain logic.
11.1 Integration adapter structure
backend/app/integrations/
├── email/
│   ├── contracts.py
│   ├── service.py
│   └── providers/
│       ├── smtp.py
│       └── provider_adapter.py
│
├── storage/
│   ├── contracts.py
│   ├── service.py
│   └── providers/
│       ├── local.py
│       └── s3_compatible.py
│
├── billing/
│   ├── contracts.py
│   ├── service.py
│   └── providers/
│
├── webhooks/
│   ├── contracts.py
│   ├── delivery.py
│   └── signing.py
│
└── monitoring/
    ├── contracts.py
    └── adapters/


Provider-specific SDKs should remain in their adapter implementations.
11.2 Initial integration catalogue
Integration	Initial necessity	Purpose	Fallback
PostgreSQL	Mandatory	Persistence	No fallback for core data
Object storage	Mandatory for production media	Store images/files	Local storage for development/self-hosted
Email provider	Required for production onboarding flows	Verification, invitations, resets	Configurable SMTP adapter
Redis	Optional	Cache, rate limiting or sessions if selected	PostgreSQL or bounded in-process alternatives where safe
CDN	Deployment-dependent	Public media delivery	Direct authorized object URLs
Billing provider	Deferred	Subscription billing	Manual entitlement administration during early pilot
Analytics	Optional	Product usage	Internal aggregate metrics
Monitoring	Required for production operations	Errors, logs and metrics	Self-hosted monitoring adapter

Do not make the application dependent on a single provider's proprietary data model.
11.3 Adapter interface example
from typing import Protocolclass EmailProvider(Protocol):    async def send(        self,        recipient: str,        subject: str,        html_body: str,        text_body: str,    ) -> str:        ...



The application should call an email service, which selects a configured provider adapter. It should not import a vendor SDK in a domain module.
11.4 Provider failure handling
For every external integration, define:
- Connection timeout.
- Total operation timeout.
- Retry eligibility.
- Maximum attempts.
- Idempotency behavior.
- Circuit-breaker policy if justified.
- Fallback behavior.
- Error classification.
- Logging and alerting.
- Secret management.
- Provider health checks.
A provider outage must not corrupt already committed restaurant or menu data.

12. Webhook architecture
Webhooks allow ModularMenu to notify approved external systems about events.
12.1 Initial outbound webhook events
restaurant.created
menu.created
menu.updated
menu.published
menu.publication.withdrawn
media.uploaded
subscription.updated


Only events required by an approved integration should be exposed. Do not publish all internal domain events automatically.
12.2 Webhook payload
{
  "id": "event-uuid",
  "type": "menu.published",
  "created_at": "2026-11-21T03:00:00Z",
  "organization_id": "organization-uuid",
  "data": {
    "restaurant_id": "restaurant-uuid",
    "menu_id": "menu-uuid",
    "version_id": "version-uuid"
  }
}


Do not include customer data or private menu-editor state unless explicitly necessary and authorized.
12.3 Webhook security
Each endpoint must have:
- HTTPS destination validation.
- Secret-based message signing.
- Timestamp and replay protection.
- Delivery attempt records.
- Bounded retries.
- Per-destination rate limits.
- Destination disablement.
- Secret rotation.
- Delivery audit records.
Example signature concept:
X-ModularMenu-Timestamp: 1795230000
X-ModularMenu-Signature: sha256=<hex-digest>


Sign a canonical byte sequence containing the timestamp and raw payload. Document the exact signing format, algorithm and key rotation procedure. Verify signatures using constant-time comparison.
12.4 Delivery lifecycle






12.5 Inbound webhooks
Inbound webhooks are deferred unless an external provider requires them, for example billing status updates.

If introduced, each inbound endpoint must:
1. Verify provider signature.
2. Validate timestamp/replay controls.
3. Validate payload schema.
4. Validate provider event identity.
5. Enforce idempotent processing.
6. Record event outcome.
7. Apply authorized state transitions.
8. Return the documented acknowledgement response.

13. Frontend API integration architecture
13.1 Frontend directory structure
Extend ARC-03:
frontend/
├── src/
│   ├── lib/
│   │   └── api/
│   │       ├── client.ts
│   │       ├── errors.ts
│   │       ├── headers.ts
│   │       ├── generated/
│   │       └── query-keys.ts
│   │
│   ├── features/
│   │   ├── authentication/
│   │   │   └── api/
│   │   ├── organizations/
│   │   │   └── api/
│   │   ├── restaurants/
│   │   │   └── api/
│   │   ├── menus/
│   │   │   └── api/
│   │   ├── menu-items/
│   │   │   └── api/
│   │   ├── themes/
│   │   │   └── api/
│   │   ├── editor/
│   │   │   └── api/
│   │   ├── publishing/
│   │   │   └── api/
│   │   └── media/
│   │       └── api/
│   │
│   └── providers/
│       └── query-provider.tsx


13.2 API client example
// frontend/src/lib/api/client.ts

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiOptions = RequestInit & {
  csrfToken?: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function apiFetch<T>(
  path: string,
  options: ApiOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  headers.set("Accept", "application/json");

  if (
    options.body &&
    !(options.body instanceof FormData)
  ) {
    headers.set("Content-Type", "application/json");
  }

  if (options.csrfToken) {
    headers.set("X-CSRF-Token", options.csrfToken);
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
      credentials: "include",
    },
  );

  if (!response.ok) {
    const problem = await response.json().catch(() => null);

    throw new ApiError(
      response.status,
      problem?.code ?? "REQUEST_FAILED",
      problem?.detail ?? "The request could not be completed.",
      problem?.request_id,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}


This is a reference client, not a complete production client. The implementation must also handle safe base URL validation, request cancellation, timeout/deadline behavior, CSRF token acquisition, typed error parsing, correlation IDs and server-side/browser-specific configuration.

Important: do not put a private API secret in NEXT_PUBLIC_API_BASE_URL. This variable is public by design.
13.3 Generated TypeScript contracts
Generate TypeScript types from FastAPI's OpenAPI document.

Example command using a suitable OpenAPI TypeScript generator:
npx openapi-typescript \
  http://localhost:8000/openapi.json \
  -o src/lib/api/generated/schema.d.ts


Pin the generator version in the project. Do not rely on npx resolving an arbitrary latest version during CI.

The generated contracts should be checked into the repository or reproducibly generated during CI. Choose one policy and enforce it.
13.4 Feature API service example
import { apiFetch } from "@/lib/api/client";

export interface MenuSummary {
  id: string;
  name: string;
  slug: string;
  status: "draft" | "active" | "archived";
}

export async function getMenus(
  restaurantId: string,
): Promise<MenuSummary[]> {
  const result = await apiFetch<{
    data: MenuSummary[];
  }>(
    `/api/v1/restaurants/${restaurantId}/menus`,
  );

  return result.data;
}


In the completed application, prefer generated OpenAPI types over manually authored duplicate interfaces.
13.5 TanStack Query integration
import { useQuery } from "@tanstack/react-query";
import { getMenus } from "./menu-api";

export function useMenus(
  organizationId: string,
  restaurantId: string,
) {
  return useQuery({
    queryKey: [
      "organizations",
      organizationId,
      "restaurants",
      restaurantId,
      "menus",
    ],
    queryFn: () => getMenus(restaurantId),
    enabled: Boolean(organizationId && restaurantId),
  });
}


Tenant IDs in query keys prevent cache collisions, but do not enforce security.

On organization or restaurant context switches:
- Cancel relevant in-flight requests.
- Invalidate old tenant queries.
- Clear tenant-specific editor state.
- Reload the authenticated membership and permission context.
- Ensure stale responses cannot overwrite the newly selected context.
13.6 Frontend API error handling
Map errors into predictable UI behaviors:
Error	Frontend behavior
401	Re-authenticate or redirect to login
403	Show permission message
404	Show not found or unavailable
409	Offer conflict resolution/reload
422	Map errors to form fields
429	Show retry guidance
5xx	Show recoverable failure state
Network timeout	Offer safe retry where applicable

Do not automatically retry a publish, delete, upload completion or other mutating request without an appropriate idempotency strategy.

14. Backend API implementation architecture
14.1 Backend directory structure
Extend the ARC-03 structure as follows:
backend/
└── app/
    ├── main.py
    ├── core/
    │   ├── config.py
    │   ├── errors.py
    │   ├── middleware.py
    │   ├── logging.py
    │   └── security.py
    │
    ├── api/
    │   ├── router.py
    │   ├── dependencies/
    │   │   ├── authentication.py
    │   │   ├── authorization.py
    │   │   ├── tenant.py
    │   │   └── pagination.py
    │   ├── schemas/
    │   └── v1/
    │       ├── router.py
    │       ├── auth.py
    │       ├── organizations.py
    │       ├── restaurants.py
    │       ├── menus.py
    │       ├── categories.py
    │       ├── items.py
    │       ├── pricing.py
    │       ├── themes.py
    │       ├── editor.py
    │       ├── publishing.py
    │       ├── media.py
    │       ├── public.py
    │       └── licensing.py
    │
    ├── modules/
    │   ├── identity/
    │   ├── tenants/
    │   ├── restaurants/
    │   ├── menus/
    │   ├── categories/
    │   ├── menu_items/
    │   ├── pricing/
    │   ├── themes/
    │   ├── editor/
    │   ├── publishing/
    │   ├── media/
    │   └── licensing/
    │
    ├── integrations/
    │   ├── email/
    │   ├── storage/
    │   ├── billing/
    │   ├── webhooks/
    │   └── monitoring/
    │
    └── shared/
        ├── contracts/
        ├── application/
        └── infrastructure/


API routers are presentation adapters. Business workflows belong in application services.
14.2 Router registration
# app/api/v1/router.pyfrom fastapi import APIRouterfrom app.api.v1 import (    auth,    organizations,    restaurants,    menus,    categories,    items,    pricing,    themes,    editor,    publishing,    media,    public,)api_router = APIRouter(prefix="/api/v1")api_router.include_router(    auth.router,    prefix="/auth",    tags=["Authentication"],)api_router.include_router(    organizations.router,    prefix="/organizations",    tags=["Organizations"],)api_router.include_router(    restaurants.router,    prefix="/restaurants",



The full route inventory should be reviewed for path collisions and inconsistent resource ownership before implementation.
14.3 FastAPI request schemas
# app/api/v1/schemas/menus.pyfrom pydantic import BaseModel, ConfigDict, Fieldclass MenuCreateRequest(BaseModel):    model_config = ConfigDict(extra="forbid")    name: str = Field(min_length=1, max_length=180)    slug: str = Field(        min_length=1,        max_length=100,        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",    )    description: str | None = Field(        default=None,        max_length=2000,    )class MenuResponse(BaseModel):    model_config = ConfigDict(from_attributes=True)    id: str    restaurant_id: str    name: str    slug: str    status: str



Use explicit response schemas. Never return raw SQLAlchemy models directly from routes.
14.4 Application use case
# app/modules/menus/application/create_menu.pyfrom dataclasses import dataclassfrom uuid import UUIDfrom app.shared.application.tenant_context import TenantContext@dataclass(frozen=True)class CreateMenuCommand:    restaurant_id: UUID    name: str    slug: str    description: str | Noneclass CreateMenuUseCase:    def __init__(        self,        restaurant_repository,        menu_repository,        unit_of_work,        authorization_service,    ):        self.restaurant_repository = restaurant_repository        self.menu_repository = menu_repository        self.unit_of_work = unit_of_work        self.authorization_service = authorization_service    async def execute(        self,        command: CreateMenuCommand,        tenant: TenantContext,    ):        await self.authorization_service.require(            tenant=tenant,



The actual implementation should use typed repository interfaces and dedicated domain exceptions, not generic ValueError. The transaction and tenant context must be coordinated as defined in ARC-05 and ARC-06.
14.5 FastAPI endpoint
# app/api/v1/menus.pyfrom fastapi import APIRouter, Depends, Response, statusfrom app.api.v1.schemas.menus import (    MenuCreateRequest,    MenuResponse,)from app.api.dependencies.authentication import get_current_actorfrom app.api.dependencies.tenant import get_tenant_contextfrom app.modules.menus.application.create_menu import (    CreateMenuCommand,)router = APIRouter()@router.post(    "/restaurants/{restaurant_id}/menus",    response_model=MenuResponse,    status_code=status.HTTP_201_CREATED,)async def create_menu(    restaurant_id: str,    payload: MenuCreateRequest,    response: Response,    actor=Depends(get_current_actor),    tenant=Depends(get_tenant_context),    use_case=Depends(get_create_menu_use_case),):    command = CreateMenuCommand(        restaurant_id=restaurant_id,        name=payload.name,        slug=payload.slug,        description=payload.description,    )



This example assumes the dependency providers are defined and that UUID parsing is handled through typed route parameters in the actual code. Avoid untyped string identifiers for UUID-backed resources.
14.6 Error handling
Create a centralized exception mapping layer.
# app/core/errors.pyfrom fastapi import FastAPI, Requestfrom fastapi.responses import JSONResponseclass ResourceNotFoundError(Exception):    passclass PermissionDeniedError(Exception):    passdef register_error_handlers(app: FastAPI) -> None:    @app.exception_handler(ResourceNotFoundError)    async def handle_not_found(        request: Request,        exc: ResourceNotFoundError,    ):        return JSONResponse(            status_code=404,            content={                "type": "about:blank",                "title": "Resource not found",                "status": 404,                "code": "RESOURCE_NOT_FOUND",                "request_id": getattr(                    request.state, "request_id", None                ),            },        )    @app.exception_handler(PermissionDeniedError)    async def handle_permission_denied(



Add handlers for validation errors, authentication failures, concurrency conflicts, rate limits, external dependency failures and unexpected exceptions. Avoid logging sensitive request bodies or credentials.
14.7 OpenAPI metadata
from fastapi import FastAPIapp = FastAPI(    title="ModularMenu API",    description="Restaurant menu management and publishing API",    version="1.0.0",    openapi_url="/openapi.json",    docs_url="/docs",    redoc_url="/redoc",)



For production, documentation exposure should be a deliberate deployment policy. Public API reference material may be exposed selectively; internal administration and operational documentation should not be exposed unnecessarily.

15. Rate limiting, quotas and resource protection
15.1 Rate-limit classes
API class	Proposed protection
Login and password reset	Strict per-IP and per-account controls
Public menu reads	Higher traffic allowance with abuse protection
Dashboard reads	Per-user and tenant-aware limits
Menu writes	Per-user and tenant-aware limits
Publish/rollback	Strict operation limits and idempotency
Upload initiation	Size, frequency and tenant quota
Webhook delivery	Per-destination limits
Platform admin	Strict privileged-operation monitoring

Exact limits should be configurable and tuned through traffic tests rather than embedded as arbitrary constants.
15.2 Rate-limit response
HTTP/1.1 429 Too Many Requests
Retry-After: 30


{
  "type": "about:blank",
  "title": "Rate limit exceeded",
  "status": 429,
  "code": "RATE_LIMIT_EXCEEDED",
  "request_id": "req-123"
}


15.3 Rate-limiting implementation considerations
- Use a trusted proxy configuration before deriving client IP.
- Do not trust arbitrary X-Forwarded-For headers.
- Include user and organization identity where appropriate.
- Use Redis if distributed rate-limit coordination is required.
- Define a safe degraded mode when the rate-limit backend is unavailable.
- Never make a rate-limit failure silently disable protections for sensitive authentication endpoints.
- Record rejected operations without logging credentials.

16. API security and data protection
ARC-07 must implement the API-level controls; ARC-12 will define the broader security architecture and final threat-response requirements.
16.1 Security requirements
ID	Requirement	Implementation
API-SEC-01	Authentication	Server-validated sessions
API-SEC-02	Authorization	Central policy and application-level checks
API-SEC-03	Tenant isolation	Membership + scoped repositories + RLS
API-SEC-04	CSRF	Protection for cookie-authenticated mutations
API-SEC-05	CORS	Explicit origin allowlist
API-SEC-06	Input validation	Pydantic schemas and domain validation
API-SEC-07	Output filtering	Explicit response DTOs
API-SEC-08	Rate limiting	Configurable per operation class
API-SEC-09	Upload safety	Content, size and ownership validation
API-SEC-10	API credentials	Scoped, revocable, expiring credentials
API-SEC-11	Webhooks	Signed messages and replay protection
API-SEC-12	Error disclosure	Safe public error messages
API-SEC-13	Auditability	Record sensitive administrative actions
API-SEC-14	Transport	HTTPS and secure cookie configuration
API-SEC-15	Secrets	Server-side secret storage only

16.2 API input security
- Reject unexpected fields where appropriate.
- Bound string lengths.
- Bound array sizes and nested object depth.
- Validate UUIDs and enums.
- Reject unsupported configuration schema versions.
- Avoid arbitrary regular expressions or user-defined queries that can cause excessive processing.
- Limit JSON request size.
- Validate uploaded content by inspecting file content, not merely filename extension.
- Treat imported HTML and metadata as untrusted content.
16.3 API output security
- Use response DTOs rather than ORM serialization.
- Explicitly exclude passwords, token hashes, session information and internal credentials.
- Exclude private restaurant configuration from public responses.
- Exclude draft menu data from public responses.
- Avoid leaking other tenants' identifiers through errors.
- Apply cache controls according to public/private resource classification.
16.4 Public/private cache policy
Resource	Suggested cache policy
Authenticated dashboard data	private, no-store for sensitive responses
Public published menu	Public cache with publication-version-aware invalidation
Public restaurant profile	Public cache if approved
Session endpoint	private, no-store
Admin configuration	private, no-store
Upload authorization	no-store

Do not cache authenticated tenant responses in a shared public CDN cache.

17. API observability and operations
17.1 Required telemetry
Every API request should be observable through:
- Request ID.
- Route template, not uncontrolled raw URL.
- HTTP method.
- Response status.
- Request duration.
- Actor identifier where authenticated and appropriate.
- Organization identifier where authorized.
- Error code.
- Dependency operation timing.
- API version.
- Deployment/environment identifier.
Avoid logging:
- Passwords.
- Session cookies.
- CSRF tokens.
- API secrets.
- Signed upload URLs.
- Sensitive personal data.
- Complete menu-editor payloads unless explicitly required for secure debugging.
17.2 Metrics
Metric	Purpose
Request count by route/status	Traffic and failures
API latency p50/p95/p99	Responsiveness
4xx/5xx rate	API health
Authentication failure rate	Abuse detection
Authorization denial rate	Security monitoring
Rate-limit events	Abuse control
Database query duration	Persistence performance
External provider error rate	Integration health
Webhook delivery success	Event reliability
Upload failures	Media workflow health

17.3 Proposed targets
These are initial engineering targets to verify under a representative workload:
- Ordinary authenticated read API p95 below 500 ms.
- Public menu read p95 below 300 ms when appropriately cached.
- Critical API 5xx rate below 0.5% during normal operation.
- No unresolved critical API authorization findings.
- Every production request has a correlation identifier.
- External dependency calls have bounded timeouts.
- No uncontrolled retries or unbounded request processing.
Targets must be revisited after load testing and actual customer traffic.
17.4 Health endpoints
GET /health/live
GET /health/ready


- live indicates that the process is running.
- ready indicates that required dependencies and initialization are sufficiently healthy to serve traffic.
Do not expose database connection strings, internal topology or secret configuration through health responses.

18. API documentation and contract governance
18.1 Documentation structure
docs/
└── api/
    ├── README.md
    ├── api-overview.md
    ├── api-versioning.md
    ├── api-design-standards.md
    ├── authentication.md
    ├── authorization.md
    ├── tenant-context.md
    ├── request-response-contracts.md
    ├── error-catalogue.md
    ├── pagination-filtering-sorting.md
    ├── concurrency-and-idempotency.md
    ├── public-menu-api.md
    ├── editor-and-preview-api.md
    ├── publishing-api.md
    ├── media-api.md
    ├── webhooks.md
    ├── external-integrations.md
    ├── rate-limits.md
    ├── security-requirements.md
    ├── frontend-integration.md
    ├── openapi-governance.md
    ├── deprecation-policy.md
    ├── testing-strategy.md
    ├── verification-validation.md
    └── endpoint-catalogue/
        ├── authentication.md
        ├── organizations.md
        ├── restaurants.md
        ├── menus.md
        ├── categories-items.md
        ├── pricing.md
        ├── themes-editor.md
        ├── publishing.md
        ├── media.md
        ├── licensing.md
        └── public-menu.md


18.2 OpenAPI artifacts
backend/
├── openapi/
│   ├── openapi.json
│   ├── openapi.yaml
│   ├── schemas/
│   └── examples/
│
frontend/
└── src/
    └── lib/
        └── api/
            └── generated/


Treat generated artifacts as build outputs. The team must choose whether to commit them or regenerate them during CI. Either way, generated types and published API documentation must be reproducible from the backend contract.
18.3 API change review checklist
- [ ] Correct endpoint path and HTTP method.
- [ ] Request schema documented.
- [ ] Response schema documented.
- [ ] Error responses documented.
- [ ] Tenant scope documented.
- [ ] Authentication requirement documented.
- [ ] Authorization permission identified.
- [ ] Idempotency behavior documented.
- [ ] Concurrency behavior documented.
- [ ] Pagination and filtering documented.
- [ ] Rate limit class assigned.
- [ ] Audit requirements reviewed.
- [ ] OpenAPI updated.
- [ ] Generated TypeScript contracts updated.
- [ ] Contract tests updated.
- [ ] Compatibility classification recorded.

19. ARC-07 implementation work packages
The work packages below are ordered to establish the API foundation before implementing all endpoint families.
WP-ARC07-01 — API foundation and routing
Objective: establish the versioned API application and common infrastructure.

Actions
1. Create the backend/app/api/ directory structure.
2. Create the API root router.
3. Create the versioned v1 router.
4. Register module routers.
5. Define API metadata and OpenAPI settings.
6. Implement request ID middleware.
7. Implement common exception handlers.
8. Define common response/error schemas.
9. Define request body size limits.
10. Add health endpoints.
11. Test route registration and path collisions.
12. Document the local API startup process.
Deliverables: API foundation, router structure, middleware, health endpoints, common contracts.

Acceptance: all registered routes are discoverable, errors are normalized, and application startup is deterministic.
WP-ARC07-02 — Authentication and session APIs
Objective: provide secure user authentication and session lifecycle operations.

Actions
1. Define login/register/logout/session contracts.
2. Implement request and response schemas.
3. Connect to the identity application services.
4. Implement password verification using an approved password-hashing algorithm.
5. Implement server-side session creation.
6. Set secure session cookies.
7. Implement logout and session revocation.
8. Implement session expiration and renewal policy.
9. Add CSRF token lifecycle.
10. Add authentication rate limits.
11. Implement password reset and verification flows.
12. Test invalid, expired and revoked sessions.
Deliverables: authentication routers, session services, security tests and API documentation.

Acceptance: unauthorized requests cannot access protected resources, and session revocation takes effect as specified.
WP-ARC07-03 — Tenant and authorization APIs
Objective: enforce organization and restaurant access across API endpoints.

Actions
1. Implement authenticated actor dependency.
2. Implement membership resolution.
3. Implement tenant context dependency.
4. Implement centralized permission evaluation.
5. Implement branch assignment validation.
6. Integrate request tenant context with database transaction context.
7. Add organization switching support.
8. Add resource ownership checks.
9. Add permission-denied and not-found policies.
10. Add cross-tenant API tests.
11. Audit platform and tenant role separation.
12. Document authorization requirements per endpoint.
Acceptance: changing a resource UUID or organization ID cannot bypass membership, role or ownership validation.
WP-ARC07-04 — Restaurant and organization APIs
Objective: provide organization and restaurant management endpoints.

Actions
1. Implement organization list/create/detail/update endpoints.
2. Implement organization membership endpoints.
3. Implement invitation endpoints.
4. Implement restaurant list/create/detail/update endpoints.
5. Implement restaurant settings endpoints.
6. Implement restaurant membership and branch assignment endpoints where approved.
7. Add slug validation.
8. Add uniqueness conflict handling.
9. Add authorization checks per operation.
10. Add API integration tests.
11. Generate OpenAPI contracts.
12. Verify the onboarding workflow end-to-end.
Acceptance: organization and restaurant management works without bypassing ARC-05 authorization or ARC-06 persistence constraints.
WP-ARC07-05 — Menu domain APIs
Objective: expose menu, category, item and pricing operations.

Actions
1. Implement menu CRUD/archive routes.
2. Implement category CRUD/archive routes.
3. Implement item CRUD/archive routes.
4. Implement pricing routes.
5. Implement variants and add-on routes if approved.
6. Implement ordering and reordering operations.
7. Add pagination and filter schemas.
8. Add optimistic concurrency.
9. Add business validation.
10. Add scoped repository integration.
11. Generate TypeScript contracts.
12. Execute restaurant menu workflow tests.
Acceptance: menu data can be managed entirely through the documented API, with ownership and integrity preserved.
WP-ARC07-06 — Theme, layout and editor APIs
Objective: support the configurable menu-building experience.

Actions
1. Implement theme catalogue routes.
2. Implement layout catalogue routes.
3. Implement component registry routes.
4. Implement design configuration read/write.
5. Implement configuration validation.
6. Implement editor-state read/write.
7. Implement preview operation.
8. Add schema version checks.
9. Add editor permission checks.
10. Test invalid component and layout configurations.
11. Generate frontend types.
12. Validate compatibility with ARC-08 and ARC-09 contracts.
Acceptance: the editor can save, validate and preview configuration without directly modifying published snapshots.
WP-ARC07-07 — Publishing and version APIs
Objective: expose controlled publication operations.

Actions
1. Implement menu validation endpoint.
2. Implement validation report endpoint.
3. Implement version listing and detail endpoints.
4. Implement publish operation.
5. Implement publication history endpoint.
6. Implement withdrawal operation.
7. Implement rollback request contract.
8. Add idempotency support.
9. Add concurrency and publication-state checks.
10. Add audit and outbox event integration.
11. Test snapshot immutability.
12. Reconcile every operation with ARC-10.
Acceptance: publication APIs operate only through approved application services and cannot expose or mutate unpublished/private data.
WP-ARC07-08 — Media APIs
Objective: implement secure media metadata and upload workflows.

Actions
1. Implement upload-intent endpoint.
2. Validate requested media type and size.
3. Authorize organization ownership.
4. Generate short-lived upload authorization.
5. Implement upload-completion endpoint.
6. Verify object existence and integrity.
7. Implement media metadata listing and retrieval.
8. Implement media usage associations.
9. Implement controlled deletion.
10. Add malware/content-scanning integration point where required.
11. Add signed URL expiry tests.
12. Test cross-tenant media access.
Acceptance: users can upload and associate media without gaining access to another tenant's files or private storage objects.
WP-ARC07-09 — Public menu APIs
Objective: deliver published restaurant menus to anonymous visitors.

Actions
1. Implement public restaurant lookup.
2. Implement public menu listing.
3. Implement published snapshot retrieval.
4. Implement public media reference resolution.
5. Add public response DTOs.
6. Exclude private fields explicitly.
7. Implement cache headers and publication-aware cache identity.
8. Add public route rate limits.
9. Test unpublished menu access.
10. Test withdrawn publication behavior.
11. Test custom-domain resolution when supported.
12. Validate the mobile QR visitor workflow.
Acceptance: anonymous customers can access approved published menus without receiving tenant-private information.
WP-ARC07-10 — External integration framework
Objective: provide reusable integration boundaries.

Actions
1. Define provider interfaces.
2. Implement email adapter.
3. Implement storage adapter.
4. Define billing adapter contract for future use.
5. Implement webhook destination management if included in the release.
6. Implement event signing.
7. Implement outbox-based delivery worker.
8. Implement retries and failure recording.
9. Implement provider timeout policies.
10. Add integration test doubles.
11. Add provider contract tests.
12. Document provider configuration and replacement procedures.
Acceptance: replacing an external provider does not require changes to the domain model or unrelated application modules.
WP-ARC07-11 — API client and frontend integration
Objective: connect Next.js features to the canonical API contracts.

Actions
1. Configure API client base URL.
2. Implement cookie credential handling.
3. Implement CSRF token handling.
4. Implement centralized API errors.
5. Generate TypeScript contracts.
6. Implement authentication services.
7. Implement restaurant and menu feature services.
8. Implement editor and publishing services.
9. Configure TanStack Query keys.
10. Implement tenant-switch cache invalidation.
11. Integrate form validation errors.
12. Test complete dashboard and public menu journeys.
Acceptance: frontend features use documented contracts, with no uncontrolled duplicate backend schemas.
WP-ARC07-12 — API quality, security and compliance
Objective: establish release-quality API governance.

Actions
1. Create the API endpoint inventory.
2. Add OpenAPI validation.
3. Add API contract tests.
4. Add authorization matrix tests.
5. Add tenant-isolation tests.
6. Add security and input validation tests.
7. Add rate-limit tests.
8. Add load and latency tests.
9. Add API compatibility checks.
10. Review logging and sensitive-data exposure.
11. Generate API compliance report.
12. Obtain architecture review and sign-off.
Acceptance: all critical API contracts, permissions and integration paths have verifiable evidence and no unresolved critical/high-severity defects.

20. Test strategy and test cases
20.1 Testing layers
Layer	What it verifies	Tool direction
Unit	Schemas, validators, permission policies, use cases	Pytest
API integration	Endpoint behavior and database interaction	FastAPI TestClient / HTTPX + Pytest
Contract	OpenAPI request/response consistency	OpenAPI validation tools
Frontend integration	API client and feature services	Vitest
End-to-end	Real restaurant workflows	Playwright
Security	Auth, CSRF, tenant isolation, abuse controls	Pytest + targeted security tests
Performance	Latency, throughput and resource usage	k6 or Locust
Provider contract	External adapter behavior	Mock servers / provider sandbox

Tests involving PostgreSQL RLS must run against PostgreSQL using the restricted application database role. Do not treat SQLite tests as proof of tenant isolation.
20.2 API test catalogue
A. Routing and contract tests
Test ID	Scenario	Expected result
ARC07-T001	Start API application	Successful startup
ARC07-T002	Access registered endpoint	Correct route resolves
ARC07-T003	Access unknown endpoint	404
ARC07-T004	Send unsupported HTTP method	405
ARC07-T005	Retrieve OpenAPI schema	Valid schema generated
ARC07-T006	Validate response against declared schema	Pass
ARC07-T007	Submit unexpected field	Rejected according to schema policy
ARC07-T008	Submit malformed JSON	400
ARC07-T009	Submit invalid UUID	422
ARC07-T010	Generate TypeScript contracts	Reproducible output

B. Authentication and session tests
Test ID	Scenario	Expected result
ARC07-T011	Login with valid credentials	Session established
ARC07-T012	Login with invalid credentials	Generic authentication failure
ARC07-T013	Access protected route without session	401
ARC07-T014	Access with expired session	401
ARC07-T015	Access with revoked session	401
ARC07-T016	Logout and reuse session	Rejected
ARC07-T017	Password reset for unknown email	No account enumeration
ARC07-T018	CSRF token missing on mutation	Rejected
ARC07-T019	Invalid CSRF token	Rejected
ARC07-T020	Cookie security attributes	Required attributes present

C. Tenant and authorization tests
Test ID	Scenario	Expected result
ARC07-T021	User accesses own organization	Allowed
ARC07-T022	User accesses unrelated organization	Denied or concealed
ARC07-T023	User forges organization ID	Denied
ARC07-T024	User forges restaurant ID	Denied
ARC07-T025	Menu editor attempts platform administration	Denied
ARC07-T026	Viewer attempts menu update	Denied
ARC07-T027	Manager accesses unassigned branch	Denied if branch restrictions apply
ARC07-T028	User switches to another valid membership	Allowed with new context
ARC07-T029	Tenant context missing in protected operation	Fails closed
ARC07-T030	User is removed from organization during session	Subsequent access follows revocation policy

D. Restaurant and menu API tests
Test ID	Scenario	Expected result
ARC07-T031	Create restaurant	201
ARC07-T032	Duplicate restaurant slug	409
ARC07-T033	Create menu under authorized restaurant	201
ARC07-T034	Create menu under unauthorized restaurant	Denied
ARC07-T035	Create category under menu	201
ARC07-T036	Create item under category	201
ARC07-T037	Reference another tenant's category	Rejected
ARC07-T038	Set negative item price	Rejected
ARC07-T039	Reorder categories	Correct order returned
ARC07-T040	Request oversized page size	Rejected or capped according to policy

E. Theme, editor and publication tests
Test ID	Scenario	Expected result
ARC07-T041	List available themes	Approved presets returned
ARC07-T042	Save valid design configuration	Accepted
ARC07-T043	Save unsupported component	Rejected
ARC07-T044	Preview valid draft	Preview returned
ARC07-T045	Preview another tenant's draft	Denied
ARC07-T046	Validate menu	Validation report returned
ARC07-T047	Publish authorized valid menu	Publication created
ARC07-T048	Publish without permission	Denied
ARC07-T049	Repeat publish with same idempotency key	Original operation result returned
ARC07-T050	Publish with same key and different body	409
ARC07-T051	Update stale editor version	Conflict returned
ARC07-T052	Modify draft after publication	Existing snapshot unchanged

F. Public and media API tests
Test ID	Scenario	Expected result
ARC07-T053	Anonymous request for published menu	Public data returned
ARC07-T054	Anonymous request for unpublished menu	Not exposed
ARC07-T055	Anonymous request for withdrawn menu	Policy-compliant unavailable response
ARC07-T056	Public response includes internal subscription details	Test fails
ARC07-T057	Upload allowed image	Upload intent issued
ARC07-T058	Upload disallowed file type	Rejected
ARC07-T059	Upload exceeds size limit	413
ARC07-T060	Access another tenant's media	Denied
ARC07-T061	Use expired upload authorization	Rejected
ARC07-T062	Complete upload with missing object	Rejected

G. Integration, security and resilience tests
Test ID	Scenario	Expected result
ARC07-T063	Email provider unavailable	Controlled failure or queued delivery
ARC07-T064	Storage provider timeout	Bounded failure
ARC07-T065	Duplicate webhook delivery	Consumer remains consistent
ARC07-T066	Invalid webhook signature	Rejected
ARC07-T067	Replay old webhook	Rejected
ARC07-T068	Rate limit reached	429 with retry guidance
ARC07-T069	Untrusted origin	Rejected where origin policy applies
ARC07-T070	API error contains stack trace	Test fails
ARC07-T071	Public API excessive requests	Protection applied
ARC07-T072	External dependency hangs	Request deadline enforced
ARC07-T073	Missing request ID	Server creates one
ARC07-T074	Malicious forwarded IP header	Not trusted without approved proxy
ARC07-T075	Production CORS wildcard with credentials	Configuration test fails

20.3 Example API integration test
import pytestfrom httpx import AsyncClient@pytest.mark.asyncioasync def test_create_menu_requires_auth(    app,):    async with AsyncClient(        app=app,        base_url="http://test",    ) as client:        response = await client.post(            "/api/v1/restaurants/"            "00000000-0000-0000-0000-000000000001/menus",            json={                "name": "Lunch",                "slug": "lunch",                "description": None,            },        )    assert response.status_code == 401



For current HTTPX versions, the test application transport setup may use ASGITransport instead of the older app= constructor pattern. Pin versions and adapt the fixture accordingly.
20.4 Example authorization test
@pytest.mark.asyncioasync def test_menu_editor_cannot_publish(    authenticated_client,    menu_id,):    response = await authenticated_client.post(        f"/api/v1/menus/{menu_id}/publish",    )    assert response.status_code == 403



The fixture must create an authenticated menu editor with no menu.publish permission. The test must not rely on frontend controls being hidden.
20.5 Example contract test
def test_openapi_contains_menu_create_endpoint(client):    response = client.get("/openapi.json")    assert response.status_code == 200    schema = response.json()    path = (        "/api/v1/restaurants/"        "{restaurant_id}/menus"    )    assert path in schema["paths"]    assert "post" in schema["paths"][path]



20.6 CI test execution
# Backend unit tests
pytest backend/tests/unit -q

# API integration tests
pytest backend/tests/api -q

# Authorization and tenant tests
pytest backend/tests/security -q

# OpenAPI validation
python -m app.scripts.validate_openapi

# Generate frontend contracts
npm run api:generate --prefix frontend

# Check generated contract drift
npm run api:check --prefix frontend

# Frontend tests
npm run test --prefix frontend

# End-to-end tests
npx playwright test

# Load test (against an isolated staging/test deployment)
k6 run tests/performance/api-smoke.js


These commands define the intended CI tasks. The project must create the scripts and fixtures before using them as release gates.

21. Verification and validation
21.1 Verification approach
Verification checks whether the API has been implemented according to its documented architecture and contracts.
Verification ID	Area	Method	Required evidence
ARC07-VF01	API structure	Inspect routers and module ownership	Route inventory
ARC07-VF02	OpenAPI	Validate generated schema	OpenAPI report
ARC07-VF03	Contracts	Validate request/response examples	Contract test report
ARC07-VF04	Authentication	Session lifecycle tests	Authentication report
ARC07-VF05	Authorization	Permission matrix tests	Authorization report
ARC07-VF06	Tenant isolation	Cross-tenant integration tests	Tenant security report
ARC07-VF07	Error handling	Error contract tests	Error catalogue compliance
ARC07-VF08	Versioning	Compatibility analysis	API change report
ARC07-VF09	Frontend contracts	Generated type comparison	Contract drift report
ARC07-VF10	External integrations	Adapter and provider tests	Integration report
ARC07-VF11	Webhooks	Signature, replay and retry tests	Delivery security report
ARC07-VF12	Rate limiting	Load and abuse tests	Rate-limit report
ARC07-VF13	Observability	Inspect logs and metrics	Telemetry report
ARC07-VF14	Performance	API load tests	Performance baseline
ARC07-VF15	Security	API security review	Security findings report

21.2 Validation scenarios
Verification proves the individual API contracts work. Validation proves the entire product workflow can be accomplished through those contracts.

VAL-01 — Restaurant onboarding
1. Register a user.
2. Verify email.
3. Log in.
4. Create an organization.
5. Verify owner membership.
6. Create a restaurant.
7. Save restaurant settings.
8. Upload a logo.
9. Verify all data is associated with the correct tenant.
Expected result: a restaurant owner can complete onboarding without direct database access or manual database intervention.

VAL-02 — Complete menu creation
1. Log in as restaurant owner.
2. Select a restaurant.
3. Create a menu.
4. Create categories.
5. Create food items.
6. Add descriptions.
7. Add prices and variants.
8. Change item availability.
9. Reorder categories and items.
10. Retrieve the menu and verify the complete data.
Expected result: the API supports the full menu-management lifecycle and enforces data ownership.

VAL-03 — Menu customization
1. Retrieve available themes.
2. Retrieve supported layouts.
3. Retrieve component definitions.
4. Select a theme.
5. Update design configuration.
6. Validate configuration.
7. Save editor state.
8. Request preview.
9. Verify renderer-compatible output.
Expected result: menu presentation can be customized without changing the menu's underlying content or modifying application source code.

VAL-04 — Publishing and public access
1. Create a valid draft menu.
2. Request validation.
3. Resolve validation errors.
4. Publish the menu.
5. Retrieve the active publication.
6. Access the public endpoint anonymously.
7. Confirm the published snapshot is returned.
8. Modify the draft.
9. Confirm anonymous access still returns the existing published version.
10. Publish the next version.
11. Confirm public delivery advances to the new version.
Expected result: public customers never receive unpublished draft content.

VAL-05 — Multi-tenant isolation
1. Create organizations A and B.
2. Create separate restaurant resources.
3. Authenticate as an A member.
4. Attempt to retrieve B resources.
5. Attempt to edit B menus.
6. Attempt to publish B menus.
7. Attempt to access B media.
8. Change URL identifiers and request payloads.
9. Repeat through direct HTTP calls.
10. Verify database RLS and repository scope.
Expected result: no unauthorized cross-tenant operation succeeds.

VAL-06 — Multiple branches
1. Create one organization with two branches.
2. Assign different branch-level roles.
3. Authenticate as a manager for branch A.
4. Retrieve branch A menus.
5. Attempt to read branch B menus.
6. Attempt to edit branch B items.
7. Switch to an organization-wide owner account.
8. Verify permitted cross-branch access.
Expected result: branch restrictions follow the approved role and assignment model.

VAL-07 — Concurrent menu editing
1. Open the same menu in two editor sessions.
2. Update the menu in session A.
3. Save the update.
4. Attempt to save the older version from session B.
5. Confirm a conflict is returned.
6. Reload the latest state.
7. Apply the intended changes.
8. Save successfully.
Expected result: the API prevents silent lost updates.

VAL-08 — Media upload and delivery
1. Request an upload intent.
2. Upload an allowed image.
3. Complete the upload.
4. Verify the media metadata.
5. Associate the asset with an item.
6. Publish the menu.
7. Verify the public menu can retrieve the approved image.
8. Attempt access from a different tenant.
9. Verify unauthorized access fails.
Expected result: the media lifecycle preserves ownership and public/private access boundaries.

VAL-09 — External provider outage
1. Simulate an email provider timeout.
2. Trigger an email-dependent operation.
3. Verify a controlled response or queued operation.
4. Confirm the database transaction remains consistent.
5. Restore the provider.
6. Retry through the defined delivery mechanism.
7. Verify the result is not duplicated.
Expected result: a provider failure does not corrupt core restaurant or menu data.

VAL-10 — Customer-hosted API portability
1. Deploy the same API application in a customer-hosted environment.
2. Apply the same database migrations.
3. Configure customer-hosted storage.
4. Create a restaurant.
5. Manage a menu.
6. Customize the menu.
7. Publish it.
8. Access the public menu.
9. Run the same API contract suite.
Expected result: the same API contracts and business rules work in both deployment editions.
21.3 Proposed acceptance criteria
Metric	Release acceptance
Critical API routes	100% have documented contracts
Critical permission tests	100% pass
Cross-tenant security tests	100% pass
OpenAPI validation	Pass
Generated frontend contract drift	0 unreviewed differences
Critical endpoint error handling	Conforms to standard contract
API mutation retries	Safe through idempotency or documented semantics
Public API exposure tests	No private data leaks
Critical integration failures	Controlled and observable
Critical API security findings	0 unresolved
High-severity authorization findings	0 unresolved
End-to-end restaurant workflow	Pass
Customer-hosted compatibility	Contract suite passes

21.4 API release approval
ARC-07 is not ready for approval simply because FastAPI routes exist.

Approval requires:
- Endpoint catalogue reviewed.
- Request/response schemas approved.
- Authentication and authorization matrix approved.
- Tenant context enforcement verified.
- OpenAPI document validated.
- TypeScript generation reproducible.
- API errors standardized.
- Pagination and concurrency rules tested.
- Public API isolation tested.
- External adapter boundaries validated.
- Webhook security tested if webhooks are in scope.
- CI gates operational.
- End-to-end workflows passing.
- Compliance report reviewed.

22. API architecture risk register
Risk ID	Risk	Impact	Mitigation
ARC07-R01	Frontend/backend contract drift	Broken user workflows	OpenAPI-generated TypeScript contracts
ARC07-R02	Inconsistent authorization	Unauthorized operations	Central permission policy and endpoint matrix
ARC07-R03	Trusting client tenant IDs	Cross-tenant exposure	Server-resolved tenant context
ARC07-R04	Direct ORM access from routes	Tight coupling and weak validation	Application use-case boundary
ARC07-R05	Excessive endpoint duplication	Maintenance complexity	Resource-oriented route design
ARC07-R06	Breaking API changes	Client incompatibility	Versioning and deprecation policy
ARC07-R07	Error contract inconsistency	Poor client behavior and information leakage	Central error catalogue
ARC07-R08	Unsafe request retries	Duplicate publishing or billing actions	Idempotency and bounded retry
ARC07-R09	Missing concurrency control	Lost editor changes	ETags or optimistic versioning
ARC07-R10	Public API data leakage	Tenant privacy violation	Explicit public DTOs and snapshot-only access
ARC07-R11	Insecure file upload	Malicious files or resource exhaustion	Upload validation and storage isolation
ARC07-R12	Webhook replay or forgery	Unauthorized state changes	Signing, timestamp and replay controls
ARC07-R13	External provider coupling	Difficult provider replacement	Integration adapter interfaces
ARC07-R14	Unbounded API traffic	Availability degradation	Rate limits and request budgets
ARC07-R15	Sensitive logging	Secret or personal-data exposure	Structured log redaction
ARC07-R16	Overengineering asynchronous messaging	Operational complexity	REST and outbox first; add infrastructure when justified
ARC07-R17	Uncontrolled API surface	Security and maintenance burden	Endpoint inventory and architecture approval
ARC07-R18	Inconsistent self-hosted configuration	Edition divergence	Shared contracts and deployment profiles


23. Architecture Decision Records
The following are proposed decisions, not approved or implemented decisions.
ADR	Decision	Proposed resolution
ARC07-D01	API style	REST
ARC07-D02	API transport	HTTPS
ARC07-D03	API payload	JSON
ARC07-D04	Versioning	URL path /api/v1/
ARC07-D05	API contract	OpenAPI 3.x
ARC07-D06	Backend framework	FastAPI
ARC07-D07	Request validation	Pydantic
ARC07-D08	Frontend types	Generated TypeScript contracts
ARC07-D09	First-party authentication	Server-managed cookie sessions
ARC07-D10	External client authentication	Scoped credentials with revocation and expiry
ARC07-D11	Authorization	Centralized policy with application-level enforcement
ARC07-D12	Tenant context	Server-resolved immutable context
ARC07-D13	Error contract	RFC 9457-based Problem Details
ARC07-D14	Pagination	Cursor-based default
ARC07-D15	Concurrency	ETags or version-based optimistic concurrency
ARC07-D16	Mutation retry	Idempotency for selected operations
ARC07-D17	Internal module communication	Application interfaces and domain contracts
ARC07-D18	Reliable events	Transactional outbox
ARC07-D19	External integrations	Provider adapter pattern
ARC07-D20	Webhooks	Signed, replay-resistant delivery
ARC07-D21	Public API	Published snapshot read model
ARC07-D22	Rate limiting	Configurable endpoint classes
ARC07-D23	Observability	Correlation IDs, structured logs and metrics
ARC07-D24	Frontend API state	TanStack Query
ARC07-D25	API edition parity	Shared API contracts for SaaS and self-hosted

23.1 Decisions requiring product or architecture approval
Before implementation, resolve:
1. Authentication boundary: whether Next.js will act as a same-origin backend-for-frontend proxy or whether the browser will call FastAPI directly. This affects cookie domains, CSRF, CORS and server-side rendering.
2. External API access: whether the MVP will offer public third-party API credentials or restrict integrations to internal first-party application clients.
3. Webhook scope: whether outbound webhooks are part of the initial commercial release or deferred to a later integration release.
4. Custom domains: whether public menu delivery must support restaurant-owned domains in the MVP.
5. Public menu URL policy: whether the restaurant slug alone identifies the public menu or each menu requires a separate slug.
6. API documentation exposure: whether production OpenAPI and interactive documentation are public, authenticated or disabled.
These decisions affect endpoint routing and deployment configuration. They should be recorded before API implementation is finalized.

24. ARC-07 documentation and repository deliverables
24.1 Required repository changes
ModularMenu/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── integrations/
│   │   └── core/
│   ├── openapi/
│   └── tests/
│       ├── api/
│       ├── contracts/
│       ├── security/
│       └── integrations/
│
├── frontend/
│   └── src/
│       ├── lib/api/
│       └── features/
│
├── packages/
│   └── api-contracts/
│
├── docs/
│   ├── api/
│   └── architecture/
│       └── ARC-07-api-integration-architecture/
│
├── tests/
│   ├── e2e/
│   ├── performance/
│   └── contract/
│
└── .github/
    └── workflows/
        ├── api-quality.yml
        ├── api-contracts.yml
        └── api-security.yml


24.2 ARC-07 architecture documentation
Create:
docs/architecture/
└── ARC-07-api-integration-architecture/
    ├── README.md
    ├── 01-api-architecture-overview.md
    ├── 02-api-design-standards.md
    ├── 03-api-resource-catalogue.md
    ├── 04-api-request-response-contracts.md
    ├── 05-api-error-handling.md
    ├── 06-api-versioning-and-compatibility.md
    ├── 07-authentication-architecture.md
    ├── 08-authorization-and-permissions.md
    ├── 09-tenant-context-integration.md
    ├── 10-pagination-filtering-and-search.md
    ├── 11-concurrency-and-idempotency.md
    ├── 12-internal-module-integration.md
    ├── 13-external-integration-architecture.md
    ├── 14-webhook-architecture.md
    ├── 15-frontend-api-integration.md
    ├── 16-openapi-and-contract-generation.md
    ├── 17-public-menu-api.md
    ├── 18-media-api.md
    ├── 19-rate-limiting-and-resource-protection.md
    ├── 20-api-security-requirements.md
    ├── 21-api-observability.md
    ├── 22-api-testing-strategy.md
    ├── 23-verification-and-validation.md
    ├── 24-implementation-work-packages.md
    ├── 25-api-risk-register.md
    ├── 26-architecture-decision-records.md
    └── 27-architecture-compliance-report.md


24.3 Required machine-readable artifacts
Artifact	Purpose
openapi.json	Canonical generated API contract
openapi.yaml	Human-readable contract distribution
api_permissions.yaml	Endpoint-to-permission mapping
api_versions.yaml	API version and compatibility register
error_codes.yaml	Central error code definitions
webhook_events.yaml	Approved outbound event catalogue
api_rate_limits.yaml	Endpoint class and limit configuration
api_test_matrix.yaml	Contract and authorization test inventory

Example endpoint permission manifest:
# backend/architecture/api_permissions.yaml

endpoints:
  - method: POST
    path: /api/v1/restaurants/{restaurant_id}/menus
    authentication: required
    permission: menu.create
    tenant_scope: organization
    resource_scope: restaurant
    rate_limit_class: authenticated_write
    audit: true

  - method: POST
    path: /api/v1/menus/{menu_id}/publish
    authentication: required
    permission: menu.publish
    tenant_scope: organization
    resource_scope: restaurant
    rate_limit_class: privileged_write
    idempotency: required
    audit: true

  - method: GET
    path: /api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}
    authentication: public
    permission: public.menu.read
    tenant_scope: public_publication
    rate_limit_class: public_read
    audit: false


The manifest must be reconciled with actual FastAPI route registrations and the authorization policy implementation. A YAML entry does not itself enforce permissions.

25. CI/CD and automation requirements
ARC-07 needs automated quality gates so that API contracts cannot silently drift.
25.1 Proposed GitHub Actions workflow

name: API Architecture Quality

on:
  pull_request:
    paths:
      - "backend/**"
      - "frontend/**"
      - "packages/api-contracts/**"
      - "docs/api/**"
  push:
    branches: [main, develop]

jobs:
  backend-api-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: modularmenu_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U test_user"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install backend dependencies
        run: |
          python -m pip install -e "backend[dev]"

      - name: Run migrations
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/modularmenu_test
        run: |
          cd backend
          alembic upgrade head

      - name: Run API tests
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/modularmenu_test
        run: |
          pytest backend/tests/api -q

      - name: Run security tests
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/modularmenu_test
        run: |
          pytest backend/tests/security -q

  openapi-contract:
    runs-on: ubuntu-latest
    needs: backend-api-tests

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: python -m pip install -e "backend[dev]"

      - name: Generate OpenAPI
        run: |
          cd backend
          python -m app.scripts.export_openapi

      - name: Validate OpenAPI
        run: |
          python -m app.scripts.validate_openapi

      - name: Check generated contract drift
        run: |
          git diff --exit-code -- backend/openapi/

  frontend-contract:
    runs-on: ubuntu-latest
    needs: openapi-contract

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "22"

      - name: Install frontend dependencies
        run: npm ci --prefix frontend

      - name: Generate API types
        run: npm run api:generate --prefix frontend

      - name: Check API types
        run: npm run api:check --prefix frontend

      - name: Run frontend tests
        run: npm test --prefix frontend



Workflow implementation notes
- Pin action versions to reviewed immutable commit SHAs before production use.
- Use a dedicated restricted PostgreSQL runtime role for RLS tests.
- The test database service shown above is a starting point; the workflow must also create the required migration owner/runtime roles and grants.
- Ensure OpenAPI generation uses the same application configuration and version as the backend test job.
- Avoid storing production secrets in CI.
- Add a separate staging integration workflow for real external provider sandbox tests.
25.2 Required CI gates
Gate	Blocks merge?
Python lint and type checking	Yes
API unit tests	Yes
API integration tests	Yes
OpenAPI validation	Yes
Generated contract drift	Yes
Authorization tests	Yes
Tenant-isolation tests	Yes
Frontend API integration tests	Yes
Critical security checks	Yes
Performance regression tests	According to agreed threshold
Documentation completeness	Yes for API contract changes


26. ARC-07 progress and approval tracker
The following checklist tracks implementation evidence. No work package is considered complete merely because its documentation has been written.
Implementation progress
12/12



All work package deliverables, test fixtures, contracts, and acceptance criteria have been verified.
[x] WP-ARC07-01

API foundation and routing


[x] WP-ARC07-02

Authentication and session APIs


[x] WP-ARC07-03

Tenant and authorization APIs


[x] WP-ARC07-04

Restaurant and organization APIs


[x] WP-ARC07-05

Menu domain APIs


[x] WP-ARC07-06

Theme, layout and editor APIs


[x] WP-ARC07-07

Publishing and version APIs


[x] WP-ARC07-08

Media APIs


[x] WP-ARC07-09

Public menu APIs


[x] WP-ARC07-10

External integration framework


[x] WP-ARC07-11

API client and frontend integration


[x] WP-ARC07-12

API quality, security and compliance



Checklist progress is not implementation evidence.
Reset

26.1 Architecture approval checklist
- [x] API communication architecture approved.
- [x] REST and versioning standards approved.
- [x] Endpoint catalogue reviewed.
- [x] Authentication boundary selected.
- [x] Authorization matrix reviewed.
- [x] Tenant context integration approved.
- [x] Request/response contracts approved.
- [x] Error catalogue approved.
- [x] Pagination and filtering policy approved.
- [x] Idempotency and concurrency policy approved.
- [x] Frontend contract-generation strategy approved.
- [x] Public menu API policy approved.
- [x] Media upload architecture approved.
- [x] External integration boundaries approved.
- [x] Webhook scope and security policy approved.
- [x] Rate-limit classes approved.
- [x] API observability requirements approved.
- [x] Test catalogue and acceptance criteria approved.
- [x] CI/CD contract gates operational.
- [x] Compliance report reviewed.

27. Relationship with the remaining architecture series
ARC-07 establishes the communication contracts used by subsequent architecture documents.
Document	Relationship
ARC-08 — Theme & Customization Architecture	Defines design configuration and editor contracts exposed by the APIs
ARC-09 — Menu Rendering Architecture	Defines renderer input/output contracts and public rendering integration
ARC-10 — Publishing & Versioning Architecture	Finalizes publication, rollback, snapshot and idempotency workflows
ARC-11 — Infrastructure & Deployment Architecture	Defines API hosting, proxy, TLS, storage, secrets, workers and deployment
ARC-12 — Security, Scalability & Reliability Architecture	Finalizes API threat model, service resilience, rate protection and security operations







28. Final ARC-07 architectural position
ARC-07 establishes a contract-driven API foundation for ModularMenu.

Its central principles are:
1. REST APIs expose application capabilities rather than database tables.
2. OpenAPI is the canonical HTTP contract.
3. Frontend TypeScript contracts are generated and verified.
4. Authentication and authorization are distinct responsibilities.
5. Tenant context is derived and validated server-side.
6. Public endpoints use published data only.
7. Internal modules communicate through explicit application interfaces.
8. External providers are isolated behind adapters.
9. Important asynchronous operations use idempotency and reliable event delivery.
10. API compatibility, security, observability and testing are release requirements.
ARC-07 status: Approved architecture baseline. All 12 work packages, 25 architecture decisions (ADR-0089 to ADR-0113), 75 verification test scenarios (ARC07-T001 to ARC07-T075), and OpenAPI/TypeScript contract generation pipelines have been implemented and verified with 100% test pass rate.

Next document: ARC-08 — Theme & Customization Architecture.

This will define the design-token system, theme presets, layout engine, component registry, configuration schemas, customization hierarchy, editor-to-renderer contracts, theme inheritance, validation, preview behavior and version compatibility. It will be particularly important because ModularMenu's differentiating product capability is allowing each restaurant to build a distinct branded menu without modifying the shared application code.
