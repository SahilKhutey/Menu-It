ARC-03 — Application Architecture
System Architecture
Proposed Baseline
Version 1.0

Document property	Definition
Project	ModularMenu
Document ID	ARC-03
Document title	Application Architecture
Architecture level	Application and software structure
Parent documents	ARC-01 and ARC-02
Status	Approved Architectural Baseline
Implementation status	Completed & Formally Verified (10/10 Work Packages Complete)
Primary application model	Modular monolith
Frontend	Next.js, React, TypeScript
Backend	FastAPI, Python
Persistence	PostgreSQL
API architecture	Versioned REST
Deployment target	Managed SaaS and customer-hosted


1. Document purpose
ARC-03 defines the actual application architecture of ModularMenu.

ARC-01 established what the platform is.

ARC-02 established the principles, standards, and constraints governing its development.

ARC-03 establishes how the application itself will be structured and how its internal components communicate.

It defines:
- Frontend application organization.
- Backend application organization.
- Application layers and responsibilities.
- Request and response lifecycles.
- Service and repository patterns.
- Module interaction mechanisms.
- Shared packages and reusable libraries.
- Frontend/backend communication.
- Application configuration and environment handling.
- Error handling and transaction boundaries.
- Application-level testing and verification.
- Implementation and execution work packages.
The intended outcome is a coherent application architecture that can support both deployment editions without creating separate codebases.
1.1 Architectural objectives
1. Establish a modular monolith architecture.
2. Separate frontend and backend responsibilities.
3. Establish clear application-layer boundaries.
4. Prevent uncontrolled module dependencies.
5. Define standard communication contracts.
6. Centralize application orchestration.
7. Make business logic independently testable.
8. Create reusable shared packages.
9. Establish predictable request lifecycles.
10. Support managed and self-hosted deployment profiles.
11. Make the system extensible without premature microservices.
12. Provide implementation-ready architectural specifications.
1.2 Scope
Inside ARC-03
- Next.js application architecture.
- FastAPI application architecture.
- Application layer and domain layer.
- Service and repository patterns.
- API and frontend integration.
- Shared package design.
- Dependency injection.
- Error handling.
- Application configuration.
- Application-level observability.
- Testing and quality gates.
Outside ARC-03

These will be detailed in subsequent documents:
Area	Governing document
Module responsibilities and domain boundaries	ARC-04
Tenant isolation	ARC-05
Database architecture	ARC-06
API and external integrations	ARC-07
Theme and customization	ARC-08
Rendering architecture	ARC-09
Publishing architecture	ARC-10
Deployment architecture	ARC-11
Security and reliability	ARC-12

ARC-03 defines application-level patterns without prematurely finalizing the detailed contracts belonging to those documents.

2. Application architecture overview
2.1 Architectural model
Proposed architecture
 Modular monolith with independently structured frontend and backend applications.

The platform will initially operate as two principal application processes:
1. Frontend application — Next.js.
2. Backend application — FastAPI.
Supporting infrastructure:
- PostgreSQL.
- Object storage.
- Optional Redis.
- Email provider.
- Reverse proxy/CDN.
- Monitoring and logging.
The frontend and backend will remain independently deployable, but will share a coordinated application architecture.

This is not a microservices architecture.

The backend modules will initially run inside one FastAPI application process, with clear internal boundaries.
2.2 High-level application architecture
Experience layer
Platform administration

Restaurant dashboard

Visual editor

Public menu



HTTPS / REST / JSON

Frontend application — Next.js

Routes · Components · Feature modules · State · API client · Form validation

Versioned API contracts

Backend application — FastAPI modular monolith
API / Presentation Layer

Routes, request validation, authentication dependencies


Application Layer

Use cases, orchestration, transactions, authorization coordination


Domain Layer

Entities, value objects, business rules and domain events


Infrastructure Layer

Repositories, database, storage, email and external adapters



Infrastructure resources
PostgreSQL

Object storage

Optional Redis

Email provider




2.3 Architectural interaction model
The expected communication flow is:
User
 |
 v
Next.js Application
 |
 v
Frontend Feature / API Client
 |
 v
HTTPS REST Request
 |
 v
FastAPI Router
 |
 v
Application Use Case
 |
 v
Domain Rules
 |
 v
Repository Interface
 |
 v
Infrastructure Repository
 |
 v
PostgreSQL / Object Storage


The response follows the reverse path.
Important design constraint
The frontend must never connect directly to the PostgreSQL database.

It must communicate through approved backend APIs or other explicitly designed public delivery mechanisms.

The backend must not depend on Next.js components or frontend implementation details.

3. Frontend application architecture
3.1 Frontend architectural objectives
The frontend must provide three distinct user experiences while preserving a common design system and reusable application infrastructure.
Experience	Main responsibility
Platform administration	Platform operations and customer management
Restaurant dashboard	Restaurant and menu administration
Public menu	Customer-facing restaurant menu experience

The visual editor is a feature within the restaurant dashboard, but it should have a sufficiently isolated internal architecture to support more advanced editing capabilities later.
3.2 Frontend application structure
Proposed directory structure:
frontend/
│
├── app/
│   ├── (platform)/
│   │   └── platform/
│   │       ├── dashboard/
│   │       ├── restaurants/
│   │       ├── customers/
│   │       └── settings/
│   │
│   ├── (restaurant)/
│   │   └── app/
│   │       ├── dashboard/
│   │       ├── restaurants/
│   │       ├── menus/
│   │       ├── themes/
│   │       ├── editor/
│   │       └── settings/
│   │
│   ├── (public)/
│   │   └── r/
│   │       └── [restaurantSlug]/
│   │           └── [menuSlug]/
│   │
│   ├── login/
│   ├── register/
│   ├── layout.tsx
│   └── error.tsx
│
├── components/
│   ├── ui/
│   ├── shared/
│   ├── navigation/
│   ├── feedback/
│   └── layouts/
│
├── features/
│   ├── authentication/
│   ├── platform/
│   ├── restaurants/
│   ├── menus/
│   ├── categories/
│   ├── menu-items/
│   ├── themes/
│   ├── layouts/
│   ├── editor/
│   └── publishing/
│
├── lib/
│   ├── api/
│   ├── auth/
│   ├── config/
│   ├── errors/
│   └── utilities/
│
├── hooks/
├── providers/
├── tests/
├── public/
└── package.json


Route groups in parentheses are organizational and do not form part of the public URL.

For example:
- /platform/dashboard
- /app/dashboard
- /r/cafe-example/main-menu
3.3 Frontend layer responsibilities
A. Routing layer
Responsible for:
- Page routing.
- Dynamic restaurant and menu routes.
- Route-level layouts.
- Loading boundaries.
- Error boundaries.
- Public versus protected route organization.
It must not contain complex business logic.
B. Page composition layer
Responsible for composing feature components into screens.

Example:
export default function MenuManagementPage() {
  return (
    <DashboardLayout>
      <MenuManagementHeader />
      <MenuList />
    </DashboardLayout>
  );
}


Page components should remain relatively thin.
C. Feature layer
Contains functionality associated with a business capability.

Example:
features/menus/
├── components/
│   ├── menu-list.tsx
│   ├── menu-form.tsx
│   └── menu-card.tsx
├── hooks/
│   └── use-menus.ts
├── services/
│   └── menu-api.ts
├── schemas/
│   └── menu-schema.ts
├── types/
│   └── menu.ts
└── index.ts


Rules:
- Feature-specific components remain within the feature.
- Feature services use the shared API client.
- Feature types should be explicit.
- Cross-feature imports must use approved public exports.
- Feature components must not directly access infrastructure.
D. Shared UI layer
Contains reusable elements:
- Buttons.
- Inputs.
- Dialogs.
- Cards.
- Dropdowns.
- Tables.
- Form controls.
- Notifications.
- Loading indicators.
- Empty states.
Shared UI components should not contain restaurant-specific business rules.
E. Application state layer
Use state according to its responsibility rather than placing everything in one global store.
State type	Proposed mechanism
Server data	TanStack Query
Local component state	React state
Editor working state	Dedicated editor store
URL/navigation state	URL parameters
Form state	React Hook Form, if adopted
Authentication context	Server-managed session and minimal client context
Theme preview state	Theme/editor state

Do not duplicate the same server data independently in multiple global stores.
F. API client layer
All frontend API calls should go through a shared client.

It handles:
- Base URL.
- Credentials.
- Request headers.
- Request serialization.
- Response parsing.
- Error normalization.
- Request cancellation.
- Request correlation identifiers where appropriate.
Feature services should use this client rather than directly constructing fetch logic repeatedly.
3.4 Rendering strategy
Use Next.js server and client components intentionally.
Screen/function	Proposed rendering
Public menu	Server-rendered initial experience
Public menu interactions	Client components where required
Restaurant dashboard	Authenticated server shell + client interactions
Visual editor	Client-heavy interactive experience
Platform administration	Server shell + client data interactions
Login/register	Server route with client form interactions as needed

Avoid turning the entire application into one client-side component tree.

Public menu pages should prioritize initial loading speed, SEO where applicable, accessibility, and mobile performance.
3.5 Frontend example: shared API client

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("API base URL is not configured");
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...init,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    }
  );

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));

    throw new ApiError(
      response.status,
      body?.error?.code ?? "REQUEST_FAILED",
      body?.error?.message ?? "Request failed"
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}



Implementation notes:
- This is a starting example, not a complete production client.
- API_BASE_URL must be a trusted, validated URL.
- CSRF protections must be implemented for cookie-authenticated state-changing requests.
- Do not blindly retry non-idempotent requests.
- Handle non-JSON error responses safely.
- Server-side calls and browser-side calls may need separate client adapters so that private environment variables and session credentials are handled safely.
3.6 Frontend example: feature service

import { apiRequest } from "@/lib/api/client";

export interface Menu {
  id: string;
  name: string;
  description?: string | null;
}

export interface CreateMenuInput {
  name: string;
  description?: string;
}

export const menuService = {
  list: (restaurantId: string) =>
    apiRequest<Menu[]>(
      `/api/v1/restaurants/${restaurantId}/menus`
    ),

  create: (restaurantId: string, data: CreateMenuInput) =>
    apiRequest<Menu>(
      `/api/v1/restaurants/${restaurantId}/menus`,
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    ),
};



The server must independently establish that the current user can access the specified restaurant. The path identifier is not an authorization credential.

4. Backend application architecture
4.1 Backend architectural objectives
The backend must provide a structured environment for implementing the platform's business capabilities.

It must:
- Receive and validate API requests.
- Authenticate and authorize requests.
- Coordinate application use cases.
- Enforce domain rules.
- Manage persistence.
- Coordinate external integrations.
- Manage transactions.
- Produce consistent API responses.
- Support automated testing.
- Maintain clear module boundaries.
4.2 Backend architecture pattern
The recommended pattern is a modular monolith using a layered architecture with dependency inversion.

The backend must not become a collection of unrelated route handlers and database models.

Each module should own its own application and domain behavior.
4.3 Proposed backend directory structure
backend/
│
├── app/
│   │
│   ├── main.py
│   ├── bootstrap.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── exceptions.py
│   │   ├── middleware.py
│   │   └── dependencies.py
│   │
│   ├── modules/
│   │   │
│   │   ├── identity/
│   │   ├── tenants/
│   │   ├── restaurants/
│   │   ├── menus/
│   │   ├── categories/
│   │   ├── menu_items/
│   │   ├── pricing/
│   │   ├── themes/
│   │   ├── layouts/
│   │   ├── components/
│   │   ├── editor/
│   │   ├── publishing/
│   │   ├── media/
│   │   └── licensing/
│   │
│   ├── shared/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   ├── contracts/
│   │   └── utilities/
│   │
│   └── infrastructure/
│       ├── database/
│       ├── storage/
│       ├── email/
│       ├── cache/
│       └── observability/
│
├── migrations/
├── tests/
├── scripts/
├── pyproject.toml
├── requirements.txt
└── Dockerfile


4.4 Internal module structure
Each module follows a standard organization.
modules/menus/
│
├── api/
│   ├── routes.py
│   └── dependencies.py
│
├── application/
│   ├── commands/
│   ├── queries/
│   ├── services/
│   └── interfaces/
│
├── domain/
│   ├── entities.py
│   ├── value_objects.py
│   ├── rules.py
│   ├── events.py
│   └── exceptions.py
│
├── infrastructure/
│   ├── models.py
│   ├── repositories.py
│   └── mappings.py
│
├── schemas/
│   ├── requests.py
│   └── responses.py
│
└── tests/
    ├── unit/
    └── integration/


A small module does not need every directory immediately. The structure should expand as its actual responsibilities require it, not create empty abstractions everywhere.
4.5 Backend layer responsibilities
Layer 1 — API / Presentation
Responsibilities:
- HTTP routes.
- Request parsing.
- Request validation.
- Authentication dependencies.
- Response serialization.
- HTTP status codes.
- API error mapping.
Must not:
- Implement complex business workflows.
- Perform unrelated database queries.
- Bypass application services.
- Contain domain-specific transaction logic.
Layer 2 — Application
Responsibilities:
- Coordinate use cases.
- Check application-level permissions.
- Load required domain objects.
- Invoke domain behavior.
- Manage transaction boundaries.
- Coordinate multiple modules through approved interfaces.
- Return application results.
Example use cases:
CreateRestaurant
CreateMenu
UpdateMenu
AddCategory
AddMenuItem
UpdateThemeConfiguration
PreviewMenu
PublishMenu
RollbackPublication


Layer 3 — Domain
Responsibilities:
- Business rules.
- Entity behavior.
- Value objects.
- Domain invariants.
- Domain events.
- Domain-specific exceptions.
Examples:
- A menu must belong to a restaurant.
- A published snapshot cannot be edited.
- A menu item price must comply with the currency policy.
- A component configuration must comply with its approved schema.
Domain rules should be independently testable.
Layer 4 — Infrastructure
Responsibilities:
- SQLAlchemy implementations.
- PostgreSQL connection management.
- Object storage.
- Redis adapter.
- Email delivery.
- External service adapters.
- Database transactions and persistence implementations.
Infrastructure implements the interfaces used by application and domain logic. The domain must not import infrastructure implementations.

5. Application-layer responsibilities and use-case orchestration
This section defines how a user action moves through the application.
5.1 Application service pattern
An application service represents an operation the system performs.

It coordinates domain behavior and infrastructure interfaces.

Example: CreateMenu.
HTTP Request
     |
     v
CreateMenuRoute
     |
     v
Authentication Dependency
     |
     v
Restaurant Authorization
     |
     v
CreateMenuUseCase
     |
     v
Menu Domain Validation
     |
     v
Menu Repository
     |
     v
Database Transaction
     |
     v
Menu Response


5.2 Example application use case
from dataclasses import dataclassfrom uuid import UUID, uuid4@dataclass(frozen=True)class CreateMenuCommand:    restaurant_id: UUID    name: str    description: str | None@dataclass(frozen=True)class MenuResult:    id: UUID    restaurant_id: UUID    name: strclass CreateMenuUseCase:    def __init__(        self,        restaurant_repository,        menu_repository,        unit_of_work,        authorization_service,    ):        self.restaurants = restaurant_repository        self.menus = menu_repository        self.uow = unit_of_work        self.authorization = authorization_service    async def execute(        self,        command: CreateMenuCommand,        actor_id: UUID,



This illustrates the pattern rather than a final production implementation. The repository contract, domain entity, transaction implementation, and exception types must be explicitly defined before this code is adopted.
5.3 Command and query separation
Use commands for operations that change application state.

Use queries for operations that retrieve data.
Command	Query
CreateMenu	GetMenu
UpdateMenu	ListMenus
DeleteMenu	GetMenuDetails
PublishMenu	GetPublicationHistory
UpdateTheme	GetThemeConfiguration

This is a lightweight separation of command and query responsibilities. It does not require introducing a full CQRS infrastructure.
5.4 Domain events
Domain events may be used when one business operation needs to communicate a completed domain change.

Examples:
- RestaurantCreated
- MenuCreated
- MenuUpdated
- MenuPublished
- PublicationRolledBack
Initial implementation should avoid introducing a distributed event bus.

For events that must reliably survive a database transaction, use a transactional outbox pattern when the relevant architecture requires it.

Example:
Application Use Case
        |
        v
Database Transaction
  |             |
  v             v
Business      Outbox Event
Data          Record
  |             |
  +------+------+
         |
         v
      Commit
         |
         v
Outbox Processor
         |
         v
External Notification / Cache Invalidation


This avoids treating an in-memory event dispatch as a reliable guarantee of delivery.

6. Request and response lifecycle
6.1 Standard request lifecycle
Every protected API request must follow a predictable processing sequence.
1. Incoming request
   
   Request reaches the API through the trusted ingress layer.
2. Middleware
   
   Request ID, logging context, security headers and applicable rate limiting.
3. Authentication
   
   Establish the requesting identity or determine that the route is public.
4. Request validation
   
   Validate path, query and body against defined contracts.
5. Authorization and context
   
   Establish allowed operations and authorized resource context.
6. Application use case
   
   Coordinate the business operation.
7. Domain execution
   
   Enforce business rules and invariants.
8. Persistence and integration
   
   Execute transactions and approved external operations.
9. Response mapping
   
   Convert application results or exceptions into API contracts.

6.2 Example FastAPI endpoint
from uuid import UUIDfrom fastapi import APIRouter, Depends, statusrouter = APIRouter(prefix="/menus", tags=["Menus"])@router.post(    "",    status_code=status.HTTP_201_CREATED,)async def create_menu(    payload: CreateMenuRequest,    actor=Depends(get_current_actor),    use_case=Depends(get_create_menu_use_case),):    command = CreateMenuCommand(        restaurant_id=payload.restaurant_id,        name=payload.name,        description=payload.description,    )    result = await use_case.execute(        command=command,        actor_id=actor.id,    )    return MenuResponse(        id=result.id,        restaurant_id=result.restaurant_id,        name=result.name,    )



The route delegates the business operation rather than implementing it.
6.3 Standard response model
Successful response:
{
  "data": {
    "id": "menu-uuid",
    "name": "Main Menu"
  },
  "meta": {
    "request_id": "req-123"
  }
}


Error response:
{
  "error": {
    "code": "MENU_VALIDATION_FAILED",
    "message": "The supplied menu information is invalid.",
    "details": [
      {
        "field": "name",
        "reason": "Name is required."
      }
    ],
    "request_id": "req-123"
  }
}


Exact response schemas will be finalized in ARC-07.
6.4 Error handling architecture
Errors must be classified.
Category	Example	Handling
Validation	Invalid menu name	422
Authentication	Missing/invalid session	401
Authorization	Forbidden operation	403 or controlled non-disclosure
Not found	Unknown menu	404
Conflict	Stale draft update	409
Rate limiting	Too many requests	429
Internal	Unexpected exception	500

The backend must never expose:
- Database credentials.
- SQL query internals.
- Stack traces.
- Secret values.
- Internal filesystem paths.
- Sensitive tenant information.
Detailed errors belong in protected server-side logs.

7. Service and repository patterns
7.1 Service architecture
The application should distinguish different service responsibilities rather than use one generic service class for everything.
Service type	Responsibility
Application service	Executes a business use case
Domain service	Encapsulates a business rule involving multiple domain objects
Infrastructure service	Interacts with storage, email or external systems
Authorization service	Evaluates permissions
Read/query service	Provides structured read operations

Avoid creating services without a clear responsibility.
7.2 Repository pattern
Repositories abstract persistence from application logic.

Example interface:
from typing import Protocolfrom uuid import UUIDclass MenuRepository(Protocol):    async def get_by_id(        self,        menu_id: UUID,    ):        ...    async def list_for_restaurant(        self,        restaurant_id: UUID,    ):        ...    async def add(self, menu):        ...    async def update(self, menu):        ...    async def delete(self, menu_id: UUID):        ...



Example SQLAlchemy implementation:
from sqlalchemy import selectclass SqlAlchemyMenuRepository:    def __init__(self, session):        self.session = session    async def get_by_id(self, menu_id):        statement = select(MenuModel).where(            MenuModel.id == menu_id        )        result = await self.session.execute(statement)        return result.scalar_one_or_none()    async def add(self, menu):        model = MenuModel(            id=menu["id"],            restaurant_id=menu["restaurant_id"],            name=menu["name"],            description=menu["description"],        )        self.session.add(model)        return model



This example omits tenant scoping and complete persistence behavior intentionally. The final repository contract must incorporate the security context and isolation requirements established in ARC-05 and ARC-06.
7.3 Unit of Work pattern
A Unit of Work controls transaction boundaries across repository operations.

It is useful when one use case modifies multiple records.

Example:
Create Menu
   |
   +-- Save Menu
   |
   +-- Save Default Configuration
   |
   +-- Save Audit Record
   |
   v
Commit Transaction


If a required operation fails, the transaction must roll back.

Do not create one database transaction per individual repository call when a business operation requires atomicity across several writes.
7.4 Dependency injection
Use FastAPI dependencies to construct application services and provide their required infrastructure implementations.

Example:
def get_menu_repository(    session=Depends(get_db_session),):    return SqlAlchemyMenuRepository(session)def get_create_menu_use_case(    menu_repository=Depends(get_menu_repository),    restaurant_repository=Depends(get_restaurant_repository),    unit_of_work=Depends(get_unit_of_work),    authorization=Depends(get_authorization_service),):    return CreateMenuUseCase(        restaurant_repository=restaurant_repository,        menu_repository=menu_repository,        unit_of_work=unit_of_work,        authorization_service=authorization,    )



For larger applications, the dependency construction can be centralized through explicit application providers or bootstrap functions.

Avoid global singleton repositories that retain request-specific state.

8. Shared package architecture
The frontend and backend must reuse contracts where practical, but they must not share implementation code merely for the sake of sharing.
8.1 Package organization
Proposed monorepo structure:
modularmenu/
│
├── frontend/
├── backend/
│
├── packages/
│   ├── contracts/
│   ├── shared-types/
│   ├── design-tokens/
│   ├── theme-engine/
│   ├── menu-renderer/
│   ├── component-registry/
│   ├── editor-engine/
│   └── validation/
│
├── docs/
├── infrastructure/
├── scripts/
├── tests/
│
├── docker-compose.yml
└── README.md


8.2 Package responsibilities
Package	Responsibility
contracts	Shared API contract definitions
shared-types	Shared TypeScript types generated from approved contracts
design-tokens	Design token definitions
theme-engine	Theme resolution and token transformation
menu-renderer	Public menu rendering logic
component-registry	Approved component definitions and mappings
editor-engine	Editor state and configuration operations
validation	Reusable configuration validation utilities

Not every proposed package should become an independently published package. Internal workspace packages are sufficient initially.
8.3 Shared contracts
The preferred approach is to establish backend API schemas and publish a generated TypeScript client or type definitions from the OpenAPI specification.

This reduces the risk of two independently maintained contracts drifting apart.

Example:
FastAPI Pydantic Models
          |
          v
     OpenAPI Schema
          |
          v
 TypeScript Client Generation
          |
          v
  Frontend API Integration


The generated output must be reproducible and checked into the chosen repository workflow consistently.

Do not manually maintain duplicate backend and frontend definitions without a compatibility check.
8.4 Package dependency rules
design-tokens
      |
      v
theme-engine
      |
      v
menu-renderer
      |
      v
public menu experience

component-registry
      |
      +------> menu-renderer
      |
      +------> editor-engine


The visual editor and public renderer may consume common configuration contracts, but the renderer must not depend on editor implementation details.

The backend remains authoritative for business validation.

9. Frontend/backend communication architecture
9.1 Communication model
Initial communication:
- HTTPS.
- REST.
- JSON.
- Versioned API routes.
- Cookie-based authenticated sessions, subject to the authentication design.
- OpenAPI contracts.
Do not introduce GraphQL, WebSockets, or message brokers into the initial application without a concrete requirement and ADR.
9.2 Request categories
Request category	Examples	Authentication
Public read	Published menu	Not necessarily required
Private read	Restaurant menu drafts	Required
Private write	Update item	Required
Privileged operation	Publish menu	Required + permission
Platform operation	Manage platform customers	Platform authorization
Integration operation	Webhook callback	Service authentication

9.3 Request handling standards
Every request must have:
- A defined HTTP method.
- A documented endpoint.
- A validated request contract.
- An expected response contract.
- A documented authorization policy.
- A defined error behavior.
- A traceable request identifier.
9.4 Frontend API service example

import { apiRequest } from "@/lib/api/client";

export interface MenuItem {
  id: string;
  name: string;
  description?: string | null;
  price_minor: number;
  currency: string;
}

export const menuItemService = {
  list(menuId: string) {
    return apiRequest<MenuItem[]>(
      `/api/v1/menus/${menuId}/items`
    );
  },

  update(
    menuId: string,
    itemId: string,
    payload: Partial<MenuItem>
  ) {
    return apiRequest<MenuItem>(
      `/api/v1/menus/${menuId}/items/${itemId}`,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      }
    );
  },
};



This is a contract illustration. The production implementation must use the exact approved request schemas rather than accepting arbitrary partial fields.
9.5 Authentication and CSRF interaction
For cookie-based sessions:
1. Browser receives a session cookie from the backend.
2. Cookie is configured with appropriate Secure, HttpOnly and SameSite attributes.
3. Protected requests include the session cookie automatically.
4. State-changing requests include the approved CSRF protection mechanism.
5. Backend verifies the session and CSRF requirements.
6. Backend independently authorizes the operation.
CORS must allow only the intended frontend origins and required methods/headers.

If the managed and customer-hosted editions use different domains, the cookie and origin strategy must be reviewed separately. Do not assume cross-site cookies will behave identically across browsers.

10. Application configuration and environment handling
10.1 Configuration architecture
The application must distinguish:
- Static application defaults.
- Environment-specific deployment configuration.
- Secret values.
- Tenant-specific configuration.
- User-editable restaurant configuration.
These are different configuration domains and must not be mixed.
Configuration category	Example	Storage
Application defaults	API version	Source defaults
Environment	Database host	Environment variables
Secrets	Database password	Secret manager/environment
Tenant configuration	Restaurant settings	Database
User customization	Theme tokens	Versioned database configuration

10.2 Environment structure
Development
    |
    v
Staging
    |
    v
Production


Each environment must have independent:
- Database.
- Credentials.
- Storage configuration.
- API base URLs.
- Allowed origins.
- Logging configuration.
- Integration credentials.
Production secrets must never be reused in development.
10.3 Backend settings example
from pydantic import SecretStrfrom pydantic_settings import BaseSettings, SettingsConfigDictclass Settings(BaseSettings):    app_name: str = "ModularMenu"    environment: str = "development"    debug: bool = False    database_url: SecretStr    allowed_origins: list[str] = []    redis_url: SecretStr | None = None    storage_provider: str = "local"    model_config = SettingsConfigDict(        env_file=".env",        env_file_encoding="utf-8",        extra="ignore",    )settings = Settings()



The settings object should be created once at application startup and injected through controlled dependencies.

Do not log secret values or expose them through diagnostic endpoints.

For production, configuration should be validated strictly; unexpected or missing required settings should cause a clear startup failure.
10.4 Environment variable template

# Application
APP_NAME=ModularMenu
APP_ENV=development
APP_DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/modularmenu

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Security
SESSION_SECRET=replace-with-secure-random-value
ALLOWED_ORIGINS=http://localhost:3000

# Storage
STORAGE_PROVIDER=local
LOCAL_STORAGE_PATH=./storage

# Optional cache
REDIS_URL=

# Observability
LOG_LEVEL=INFO



This is an example template only. Real credentials must never be committed. NEXT_PUBLIC_ variables are exposed to browser-side code, so secrets must never use that prefix.

The final environment-variable contract, storage adapters, and deployment profiles will be completed in ARC-11 and ARC-12.

11. Application bootstrap and startup lifecycle
11.1 Backend startup architecture
Application startup must be controlled through an explicit bootstrap process.

Responsibilities:
1. Load and validate configuration.
2. Initialize logging.
3. Initialize database connectivity.
4. Initialize infrastructure adapters.
5. Register module routers.
6. Register middleware.
7. Register exception handlers.
8. Register health endpoints.
9. Start application lifespan resources.
10. Release resources safely during shutdown.
Example:
from contextlib import asynccontextmanagerfrom fastapi import FastAPIfrom app.core.config import settingsfrom app.core.logging import configure_loggingfrom app.infrastructure.database import (    initialize_database,    close_database,)from app.api import register_routes@asynccontextmanagerasync def lifespan(app: FastAPI):    configure_logging()    await initialize_database()    yield    await close_database()def create_application() -> FastAPI:    application = FastAPI(        title=settings.app_name,        debug=settings.debug,        lifespan=lifespan,    )    register_routes(application)    return application



This assumes an asynchronous database lifecycle and a matching database implementation. The actual infrastructure adapter must be developed and tested before deployment.
11.2 Frontend startup lifecycle
The frontend must initialize:
- Application configuration.
- Shared providers.
- Query cache.
- Theme defaults.
- Route-level layouts.
- Error handling.
- Accessibility foundations.
Do not fetch private restaurant data globally for every route.

Load data at the page or feature boundary where it is required.
11.3 Health endpoints
Initial backend operational endpoints:
GET /health/live
GET /health/ready


- Liveness: whether the application process is alive.
- Readiness: whether the application can safely receive the relevant traffic.
Readiness checks should inspect required dependencies without exposing internal secrets or expensive diagnostic details.

12. Application-level implementation structure
The following defines the recommended repository organization in greater detail.
12.1 Root repository
ModularMenu/
│
├── frontend/
├── backend/
├── packages/
│
├── docs/
│   ├── architecture/
│   ├── standards/
│   ├── decisions/
│   ├── modules/
│   ├── implementation/
│   ├── testing/
│   └── reports/
│
├── infrastructure/
│   ├── docker/
│   ├── scripts/
│   └── configuration/
│
├── tests/
│   ├── architecture/
│   ├── contracts/
│   └── e2e/
│
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── CODEOWNERS
│
├── .editorconfig
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
└── README.md


12.2 Required foundational files
File	Responsibility
README.md	Project overview and entry point
.editorconfig	Consistent editor formatting
.gitignore	Exclude generated and sensitive files
.env.example	Environment variable documentation
docker-compose.yml	Local infrastructure orchestration
Makefile	Standard development commands
pyproject.toml	Backend tooling and dependencies
package.json	Frontend scripts and dependencies
CONTRIBUTING.md	Contribution procedures
ARCHITECTURE.md	Architecture entry point

12.3 Example Makefile

.PHONY: install lint test backend-test frontend-test

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm ci

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

test: backend-test frontend-test

backend-test:
	cd backend && pytest

frontend-test:
	cd frontend && npm run test -- --run

typecheck:
	cd backend && pyright
	cd frontend && npx tsc --noEmit

architecture-test:
	pytest tests/architecture -q



The commands must be aligned with the final package-manager and dependency setup.

13. Application architecture implementation work packages
The following execution plan translates ARC-03 into concrete tasks.

These are foundational architecture work packages, not permission to implement all product modules at once.
Execution plan
WP-ARC03-01 — Repository Architecture Foundation
Objective: Establish the application repository and foundational directory organization.
Actions
1. Inspect the current Git repository and branches.
2. Inspect whether frontend or backend source code already exists.
3. Record existing files and dependencies.
4. Identify reusable implementation work.
5. Create the agreed repository structure.
6. Establish frontend and backend project roots.
7. Establish the shared packages directory.
8. Create architecture documentation references.
9. Create environment templates.
10. Create development command documentation.
11. Verify that the repository can be cloned and initialized from a clean state.
Deliverables
- Repository structure.
- Root README.
- .editorconfig.
- .gitignore.
- .env.example.
- Contribution instructions.
- Application architecture index.
Test cases
ID	Test	Expected result
REPO-001	Clone repository	Successful
REPO-002	Inspect directory structure	Matches approved layout
REPO-003	Validate required documentation files	All present
REPO-004	Search tracked files for local secrets	None
REPO-005	Initialize project from clean checkout	Documented setup succeeds

Acceptance criteria
A clean repository checkout can be initialized by following the documented instructions.
WP-ARC03-02 — Frontend Application Foundation
Objective: Establish the Next.js application structure.
Actions
1. Initialize Next.js with TypeScript.
2. Enable strict TypeScript settings.
3. Configure Tailwind CSS.
4. Install and configure the selected UI component system.
5. Create route groups.
6. Create global layout.
7. Create shared UI directory.
8. Create feature module conventions.
9. Establish error and loading boundaries.
10. Configure accessibility defaults.
11. Configure linting and formatting.
12. Add frontend unit testing.
13. Establish browser test foundations.
14. Create responsive baseline layouts.
Deliverables
- Working frontend application.
- Route structure.
- Shared UI foundations.
- Feature architecture.
- Frontend tooling configuration.
- Frontend test foundation.
Test cases
ID	Test	Expected result
FE-001	Start frontend locally	Application loads
FE-002	Open platform route	Correct route resolves
FE-003	Open restaurant route	Correct route resolves
FE-004	Open public menu route	Dynamic slug resolves
FE-005	Invalid route	Appropriate not-found screen
FE-006	Test mobile viewport	No critical layout overflow
FE-007	Run TypeScript checker	No blocking type errors
FE-008	Run frontend unit tests	Tests pass

WP-ARC03-03 — Backend Application Foundation
Objective: Establish the FastAPI modular-monolith application.
Actions
1. Initialize Python project configuration.
2. Configure supported Python runtime.
3. Install FastAPI and Pydantic.
4. Configure SQLAlchemy and database driver.
5. Establish application factory.
6. Establish backend core configuration.
7. Establish module directory structure.
8. Implement router registration.
9. Configure middleware.
10. Configure exception handling.
11. Establish dependency injection.
12. Establish application lifespan management.
13. Add health endpoints.
14. Configure logging.
15. Add backend unit testing.
Deliverables
- Working FastAPI application.
- Application factory.
- Module registration mechanism.
- Health endpoints.
- Configuration system.
- Logging and exception handling.
- Backend test foundation.
Test cases
ID	Test	Expected result
BE-001	Start backend	Application starts
BE-002	Open API documentation	OpenAPI is generated
BE-003	Call liveness endpoint	Healthy response
BE-004	Call readiness endpoint	Correct readiness result
BE-005	Invalid configuration	Controlled startup failure
BE-006	Unexpected exception	Safe API error
BE-007	Shutdown application	Resources released
BE-008	Import application modules	No circular imports

WP-ARC03-04 — Application and Domain Layer Foundation
Objective: Establish the use-case, domain, and dependency-inversion patterns.
Actions
1. Define application service conventions.
2. Define command/query conventions.
3. Define domain entity conventions.
4. Define value object conventions.
5. Define repository interfaces.
6. Define Unit of Work interface.
7. Define application exception hierarchy.
8. Define domain exception hierarchy.
9. Define dependency injection providers.
10. Implement one representative use case.
11. Unit-test it with fake repository implementations.
12. Verify that domain logic does not import infrastructure.
The representative use case should be small and isolated, such as a basic menu creation operation using test doubles.
Deliverables
- Application layer foundation.
- Domain layer conventions.
- Repository contracts.
- Unit of Work contract.
- Example use case.
- Architecture tests.
Test cases
ID	Test	Expected result
APP-001	Execute valid use case	Success
APP-002	Execute invalid use case	Domain error
APP-003	Repository returns missing entity	Controlled not-found result
APP-004	Persistence failure	Transaction rolls back
APP-005	Run use case with fake repository	No database required
APP-006	Domain imports infrastructure	Architecture check fails

WP-ARC03-05 — API and Frontend Integration Foundation
Objective: Establish consistent communication between Next.js and FastAPI.
Actions
1. Define the API base path.
2. Establish API response conventions.
3. Establish error response conventions.
4. Configure CORS for approved development origins.
5. Establish frontend API client.
6. Establish backend OpenAPI generation.
7. Establish TypeScript type generation.
8. Add request correlation identifiers.
9. Add authentication integration placeholders.
10. Define CSRF requirements for state-changing requests.
11. Add frontend/backend integration tests.
12. Verify that the frontend handles backend failures safely.
Deliverables
- API client.
- OpenAPI specification.
- Generated client/types workflow.
- CORS policy.
- Error normalization.
- Integration tests.
Test cases
ID	Test	Expected result
INT-001	Frontend calls backend health API	Success
INT-002	Backend returns validation error	Correct frontend error
INT-003	Backend unavailable	Controlled UI failure
INT-004	Unapproved origin	CORS blocks browser access
INT-005	OpenAPI type generation	Reproducible output
INT-006	API contract changes	Compatibility review detects drift
INT-007	State-changing cookie request without CSRF proof	Rejected after security integration

WP-ARC03-06 — Shared Package Architecture
Objective: Establish shared frontend packages and contract generation.
Actions
1. Select workspace management approach.
2. Create shared package directory.
3. Define package naming rules.
4. Define package ownership.
5. Establish package export conventions.
6. Define shared contract generation.
7. Create design-token package.
8. Establish shared configuration types.
9. Define package dependency rules.
10. Add package-level unit tests.
11. Verify package consumption from frontend features.
12. Verify that editor and renderer do not create circular dependencies.
Deliverables
- Shared package foundation.
- Contract generation process.
- Shared design-token package.
- Package dependency policy.
- Package testing framework.
Test cases
ID	Test	Expected result
PKG-001	Import shared package	Successful
PKG-002	Build shared package	Successful
PKG-003	Introduce circular package dependency	Rejected
PKG-004	Generate TypeScript contracts	Reproducible
PKG-005	Change backend schema	Contract change is detected
PKG-006	Test package independently	Tests run without full application

WP-ARC03-07 — Configuration and Bootstrap Foundation
Objective: Establish predictable application startup and configuration handling.
Actions
1. Define configuration namespaces.
2. Define required and optional variables.
3. Define configuration validation.
4. Establish environment-specific defaults.
5. Implement backend settings loader.
6. Establish frontend configuration validation.
7. Implement startup and shutdown handling.
8. Implement health endpoints.
9. Establish dependency initialization.
10. Test missing required configuration.
11. Test optional infrastructure unavailability.
12. Document local startup procedures.
Test cases
ID	Test	Expected result
CFG-001	Valid configuration	Startup succeeds
CFG-002	Missing required database URL	Startup fails clearly
CFG-003	Invalid storage provider	Controlled failure
CFG-004	Missing optional Redis	Core application can operate
CFG-005	Secret appears in logs	Security test fails
CFG-006	Production debug enabled	Deployment validation rejects configuration

WP-ARC03-08 — Application Observability and Error Management
Objective: Establish traceable application behavior and safe failure handling.
Actions
1. Define structured log format.
2. Add request IDs.
3. Define log levels.
4. Add request lifecycle logging.
5. Establish exception mapping.
6. Establish error response contracts.
7. Add health and readiness checks.
8. Add database error logging.
9. Add external integration error logging.
10. Prevent secret leakage.
11. Define error severity.
12. Add tests for exception handling.
Test cases
ID	Test	Expected result
OBS-001	API request	Request ID present
OBS-002	Unhandled exception	Safe error response
OBS-003	Database error	Error logged without credentials
OBS-004	Invalid session	Correct authentication error
OBS-005	Sensitive information in exception	Not exposed publicly
OBS-006	Readiness dependency unavailable	Unready status reported

WP-ARC03-09 — Application Testing Infrastructure
Objective: Establish the automated application verification system.
Actions
1. Configure backend test runner.
2. Configure frontend test runner.
3. Establish test fixtures.
4. Establish fake repositories.
5. Establish integration-test database.
6. Establish API test client.
7. Establish frontend component tests.
8. Establish Playwright browser tests.
9. Establish architecture tests.
10. Establish coverage reporting.
11. Establish CI execution.
12. Produce initial test report.
Test cases
ID	Test	Expected result
TEST-001	Backend unit suite	Pass
TEST-002	Frontend unit suite	Pass
TEST-003	Backend integration suite	Pass
TEST-004	Contract test suite	Pass
TEST-005	Architecture suite	Pass
TEST-006	Browser smoke test	Pass
TEST-007	CI with intentionally failing test	Pipeline fails
TEST-008	Test execution report	Evidence produced

WP-ARC03-10 — Application Architecture Compliance Audit
Objective: Verify the complete application foundation against ARC-03.
Actions
1. Inspect the frontend directory structure.
2. Inspect the backend directory structure.
3. Inspect layer boundaries.
4. Inspect module dependency graph.
5. Review service and repository contracts.
6. Review application bootstrap.
7. Review API integration.
8. Review configuration handling.
9. Review observability.
10. Run all automated test suites.
11. Run security checks.
12. Review technical documentation.
13. Record architectural deviations.
14. Produce the compliance report.
15. Obtain approval before proceeding to ARC-04.
Final deliverables
docs/reports/ARC-03/
├── application-architecture-audit.md
├── frontend-architecture-report.md
├── backend-architecture-report.md
├── integration-test-report.md
├── dependency-analysis.md
├── configuration-audit.md
├── verification-report.md
├── validation-report.md
├── deviation-register.md
└── approval-record.md



14. Complete application test catalogue
This section consolidates the architecture-level acceptance tests.

The tests are to be implemented across the appropriate work packages.
14.1 Frontend tests
ID	Test scenario	Expected result
FE-ARC03-001	Route resolution	Correct screen loads
FE-ARC03-002	Unknown route	Not-found experience
FE-ARC03-003	API server unavailable	Controlled error state
FE-ARC03-004	Loading screen	Loading state displayed
FE-ARC03-005	Empty menu list	Empty state displayed
FE-ARC03-006	Invalid form	Field-level validation
FE-ARC03-007	Mobile viewport	Usable responsive layout
FE-ARC03-008	Shared UI component	Consistent design behavior
FE-ARC03-009	Type generation	Frontend contracts match API
FE-ARC03-010	Public route	No private dashboard dependency

14.2 Backend tests
ID	Test scenario	Expected result
BE-ARC03-001	Application startup	Successful
BE-ARC03-002	Invalid startup configuration	Clear failure
BE-ARC03-003	Module registration	Expected routers available
BE-ARC03-004	Valid use case	Correct result
BE-ARC03-005	Invalid domain operation	Controlled domain exception
BE-ARC03-006	Repository failure	Transaction rollback
BE-ARC03-007	Dependency injection	Correct implementation injected
BE-ARC03-008	Shutdown	Resources released
BE-ARC03-009	Unexpected exception	Standard error response
BE-ARC03-010	Domain test without infrastructure	Successful

14.3 Integration tests
ID	Test scenario	Expected result
INT-ARC03-001	Frontend health API call	Success
INT-ARC03-002	Invalid API request	Standard validation error
INT-ARC03-003	API response type mismatch	Contract check detects it
INT-ARC03-004	Database transaction failure	Rollback
INT-ARC03-005	Unauthorized operation	Denied
INT-ARC03-006	Invalid origin	Browser request blocked
INT-ARC03-007	Missing required dependency	Controlled readiness failure
INT-ARC03-008	Request correlation	Request ID traceable

14.4 Architecture tests
ID	Test scenario	Expected result
ARCH-ARC03-001	Domain imports FastAPI	Rejected
ARCH-ARC03-002	Domain imports SQLAlchemy	Rejected
ARCH-ARC03-003	API route contains persistence logic	Review/check flags it
ARCH-ARC03-004	Feature accesses another feature's private internals	Rejected
ARCH-ARC03-005	Circular package dependency	Rejected
ARCH-ARC03-006	Backend imports frontend implementation	Rejected
ARCH-ARC03-007	Renderer imports editor implementation	Rejected
ARCH-ARC03-008	Application use case depends on concrete repository	Architecture review flags it


15. Verification and validation framework
15.1 Verification
Verification asks:

Has the application been implemented according to ARC-03?

Verification activities:
1. Repository structure inspection.
2. Dependency graph analysis.
3. Layer-boundary checks.
4. Code review.
5. Static analysis.
6. Type checking.
7. Unit testing.
8. Integration testing.
9. Contract testing.
10. Startup and shutdown testing.
11. Configuration validation.
12. CI pipeline verification.
Verification acceptance
The application architecture passes verification when:
- No critical layer-boundary violations remain.
- Backend and frontend structures follow approved conventions.
- Application services are independently testable.
- API contracts are generated and validated.
- Required configuration is validated.
- Test suites pass.
- CI quality gates operate.
- All critical deviations are resolved or formally accepted.
15.2 Validation
Validation asks:

Does this application architecture support the actual ModularMenu product?

The following demonstrations should be completed.
VAL-01 — Restaurant dashboard access
1. Start the frontend.
2. Start the backend.
3. Authenticate using a test account.
4. Open the restaurant dashboard.
5. Load restaurant information through the API.
6. Verify loading and error handling.
7. Verify unauthorized access is denied.
Expected result: the dashboard operates using the defined frontend/backend communication architecture.
VAL-02 — Menu management interaction
1. Create a test restaurant.
2. Open menu management.
3. Submit a valid menu creation request.
4. Verify the backend use case executes.
5. Verify the record is persisted.
6. Reload the page.
7. Verify the record is retrieved through the API.
Expected result: the frontend, API, application service, repository, and database work together correctly.
VAL-03 — Public menu independence
1. Open the public menu route.
2. Load published menu data.
3. Verify no dashboard session is required.
4. Verify no editor state is loaded.
5. Verify responsive presentation.
Expected result: public menu delivery is independent of the administration experience.
VAL-04 — Self-hosting portability
1. Build the frontend and backend.
2. Start them using the local deployment profile.
3. Use the configured local database and storage adapter.
4. Change deployment configuration without changing application business logic.
5. Verify the same application starts.
Expected result: application code remains independent of provider-specific configuration.
VAL-05 — Application failure recovery
1. Start the application normally.
2. Stop an optional service such as Redis.
3. Execute a core application operation.
4. Verify core behavior remains available if the operation does not require Redis.
5. Stop the database.
6. Verify readiness changes appropriately.
7. Restore the database.
8. Verify recovery.
Expected result: predictable failure behavior and recovery.
15.3 Traceability matrix
Architecture requirement	Verification evidence	Validation evidence
Frontend/backend separation	Dependency checks	Integrated operation
Layered backend	Architecture tests	End-to-end use case
Application services	Unit tests	Menu creation workflow
Repository abstraction	Fake repository tests	Database persistence
Shared contracts	OpenAPI checks	Frontend integration
Bootstrap architecture	Startup tests	Clean deployment startup
Error handling	Exception tests	Failure demonstration
Configuration management	Settings tests	Deployment profile switch
Renderer independence	Import checks	Public menu operation
Test infrastructure	CI test reports	Repeatable test execution


16. Non-functional application requirements
These are proposed application-level targets, not verified production performance.
Attribute	Initial target	Testing approach
Application modularity	No unauthorized dependency cycles	Architecture analysis
Frontend reliability	No uncaught critical route errors	Browser testing
Backend reliability	Predictable startup/shutdown	Lifecycle tests
API performance	p95 under 500ms for ordinary uncached operations	Load testing
UI performance	LCP under 2.5 seconds	Performance audit
Accessibility	WCAG 2.2 AA target	Automated + manual audit
API compatibility	No unreviewed breaking changes	Contract testing
Configuration safety	Invalid required settings rejected	Startup testing
Test repeatability	Stable automated test suite	Repeated CI runs
Deployment portability	Same business logic in both editions	Deployment validation

Application-level performance must be measured using realistic workloads. A passing unit test does not establish production scalability.

17. Architectural risks and mitigation
ID	Risk	Impact	Mitigation
R03-01	Frontend becomes tightly coupled	Difficult redesign	Feature boundaries
R03-02	Backend becomes a large route collection	Unmaintainable code	Application services
R03-03	Overuse of shared packages	Excessive complexity	Share only stable contracts
R03-04	Repository abstraction becomes excessive	Development overhead	Introduce only where useful
R03-05	Premature microservices	Operational complexity	Maintain modular monolith
R03-06	Duplicate frontend/backend types	Contract drift	OpenAPI generation
R03-07	Global state becomes unmanageable	UI inconsistency	State ownership rules
R03-08	Configuration becomes fragmented	Deployment errors	Centralized validation
R03-09	External service failures propagate	Platform instability	Adapter and failure policies
R03-10	Architecture documentation diverges	Implementation confusion	Compliance review


18. ARC-03 implementation and approval tracker
The following checklist tracks the foundational architecture work. All work packages have been completed and verified with automated test suites.
ARC-03 work package tracker
10/10 Complete

[x] WP-01 Repository architecture foundation
[x] WP-02 Frontend application foundation
[x] WP-03 Backend application foundation
[x] WP-04 Application and domain layer foundation
[x] WP-05 API and frontend integration foundation
[x] WP-06 Shared package architecture
[x] WP-07 Configuration and bootstrap foundation
[x] WP-08 Application observability and error management
[x] WP-09 Application testing infrastructure
[x] WP-10 Application architecture compliance audit

18.1 Final approval criteria
ARC-03 approval status:
- [x] Frontend architecture documented and reviewed.
- [x] Backend architecture documented and reviewed.
- [x] Application layers and responsibilities defined.
- [x] Module communication rules established.
- [x] Service and repository patterns validated.
- [x] Shared package architecture established.
- [x] Frontend/backend API integration demonstrated.
- [x] Configuration and bootstrap procedures validated.
- [x] Error handling and observability tested.
- [x] Application-level test suites operational.
- [x] Architecture compliance report produced.
- [x] Critical architectural deviations resolved or accepted.

19. ARC-03 final architectural decisions
The following decisions form the approved application architecture baseline.
ID	Decision	Status
ARC03-D01	Use a modular monolith initially	Accepted (ADR-0013)
ARC03-D02	Use Next.js for frontend	Accepted (ADR-0014)
ARC03-D03	Use FastAPI for backend	Accepted (ADR-0015)
ARC03-D04	Separate frontend and backend processes	Accepted (ADR-0016)
ARC03-D05	Use layered backend architecture	Accepted (ADR-0017)
ARC03-D06	Use application services for use cases	Accepted (ADR-0018)
ARC03-D07	Use repository interfaces for persistence	Accepted (ADR-0019)
ARC03-D08	Use Unit of Work for multi-record transactions where needed	Accepted (ADR-0020)
ARC03-D09	Use REST APIs with versioning	Accepted (ADR-0021)
ARC03-D10	Generate frontend contracts from OpenAPI	Accepted (ADR-0022)
ARC03-D11	Use feature-based frontend organization	Accepted (ADR-0023)
ARC03-D12	Use shared workspace packages	Accepted (ADR-0024)
ARC03-D13	Keep Redis optional	Accepted (ADR-0025)
ARC03-D14	Centralize configuration validation	Accepted (ADR-0026)
ARC03-D15	Use automated architecture compliance tests	Accepted (ADR-0027)

Architecture review note: All 15 baseline decisions are formally accepted and documented in `docs/decisions/decision-register.md` (ADR-0013 through ADR-0027).

20. Next architecture document — ARC-04
Next in architecture sequence
ARC-04 — Modular Domain Architecture
Purpose: Define the complete domain structure of ModularMenu, including module responsibilities, boundaries, dependencies, ownership, interfaces, and domain interactions.

Proposed coverage:
1. Domain architecture overview.
2. Domain decomposition and bounded contexts.
3. Core modules and their responsibilities.
4. Module ownership and internal structures.
5. Domain entities and value objects.
6. Module interfaces and contracts.
7. Module-to-module communication.
8. Domain events and workflows.
9. Dependency and interaction matrix.
10. Module lifecycle and extensibility.
11. Domain-level testing.
12. Verification, validation and architecture compliance.

Recommended sequence: Finish ARC-03 review and establish its foundational application architecture before detailed module implementation. ARC-04 will then define exactly what each module owns and how modules interact, which is necessary before finalizing the detailed multi-tenant and data architectures in ARC-05 and ARC-06.
