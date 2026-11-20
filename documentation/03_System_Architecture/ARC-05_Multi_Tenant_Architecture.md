ARC-05 — Multi-Tenant Architecture
ModularMenu · Architecture Documentation Series
Version 1.0
Approved baseline
Implementation Complete

Document property	Value
Document ID	ARC-05
Document title	Multi-Tenant Architecture
Parent documents	ARC-01, ARC-02, ARC-03, ARC-04
Next documents	ARC-06 Data Architecture, ARC-07 API & Integration Architecture
Architecture style	Modular monolith, shared SaaS infrastructure
Primary tenancy model	Shared database and shared schema
Secondary deployment model	Customer-hosted, isolated deployment
Critical priority	P0 — Security and data isolation

1. Purpose
ARC-05 defines how ModularMenu securely supports multiple independent restaurant customers using a shared SaaS application while preserving a separate customer-hosted deployment option.

The architecture must ensure that one organization cannot access, modify, enumerate, publish, or otherwise interfere with another organization's private data.

This applies not only to database queries, but to the complete application lifecycle:
- Authentication and tenant resolution.
- Organization membership and restaurant access.
- Role-based and resource-level authorization.
- Backend request processing.
- Database access and PostgreSQL Row-Level Security.
- Background tasks and scheduled jobs.
- File uploads and object storage.
- Public menu delivery.
- Publishing and version history.
- Cache keys and invalidation.
- Analytics and integrations.
- Audit logging.
- Administrative access.
- SaaS onboarding, suspension and offboarding.
- Customer-hosted deployment isolation.
Primary security objective: Tenant isolation must be enforced by the server and persistence layer. A tenant identifier supplied by the browser, URL, request body or API client must never be treated as proof of authorization.
1.1 Architectural outcomes
ID	Objective	Expected outcome
ARC05-OBJ-01	Tenant isolation	No unauthorized cross-tenant access
ARC05-OBJ-02	Organization ownership	Each restaurant has a valid owning organization
ARC05-OBJ-03	Membership control	Users access only resources allowed by their memberships
ARC05-OBJ-04	Resource authorization	Access checks apply to individual resources and operations
ARC05-OBJ-05	Database protection	Database policies provide an additional isolation boundary
ARC05-OBJ-06	Public delivery safety	Public menus expose only intentionally published information
ARC05-OBJ-07	Storage isolation	Private files cannot be accessed across tenants
ARC05-OBJ-08	Cache isolation	Cached tenant data cannot leak between organizations
ARC05-OBJ-09	Operational isolation	Background jobs and administrative operations preserve tenant scope
ARC05-OBJ-10	Deployment portability	SaaS and self-hosted editions share the same domain logic
ARC05-OBJ-11	Auditability	Tenant-sensitive operations are attributable and traceable
ARC05-OBJ-12	Security verification	Cross-tenant access attempts are tested continuously


2. Multi-tenancy model
2.1 Proposed tenancy hierarchy
ModularMenu uses an organization as its primary tenant boundary. An organization may own one or more restaurants or restaurant branches.
ModularMenu SaaS Platform
Shared application, infrastructure and platform administration
Organization A
Tenant A
Restaurant A1
Menus, items, settings
Restaurant A2
Menus, items, settings
Restaurant A3
Menus, items, settings
Users A · Private data A · Media A


Organization B
Tenant B
Restaurant B1
Menus, items, settings
Restaurant B2
Menus, items, settings
Users B · Private data B · Media B



Organizations are isolated from one another. Multiple restaurant branches can belong to the same organization.
2.2 Tenant definition
For this architecture:
- Platform: The overall ModularMenu service and its infrastructure.
- Tenant: An organization that owns restaurant resources within the SaaS platform.
- Organization: The commercial customer account and primary isolation boundary.
- Restaurant: A business location or branch owned by an organization.
- Membership: A relationship between a user and an organization, including the user's organization-level role.
- Restaurant assignment: An optional narrower restriction determining which branches a member may manage.
- Public visitor: An unauthenticated customer accessing intentionally published restaurant information.
- Platform operator: An authorized person operating the platform, with privileges separate from tenant membership.
2.3 Why organization-level tenancy?
The organization is preferable to using a restaurant as the primary tenant because:
1. A restaurant business may own multiple branches.
2. A single owner may need to manage several branches.
3. Staff may be assigned to one or several branches.
4. Subscription and licensing may be organization-level.
5. Branding and certain settings may be shared across branches.
6. Centralized analytics may span multiple branches.
The restaurant remains a resource-level boundary within the organization.

Decision: The organization is the primary tenant. Restaurant-level authorization provides a second scope restriction.

3. Tenancy isolation strategy
3.1 Selected model — Shared database, shared schema
Proposed primary model
For the initial SaaS edition, all organizations share a PostgreSQL database and schema. Tenant-owned records contain an organization identifier, and application-level authorization and database policies enforce isolation.
Isolation model	Advantages	Disadvantages	Decision
Separate database per tenant	Strong physical separation	Expensive to operate and migrate	Not initial default
Separate schema per tenant	More logical separation	Schema migration and connection complexity	Not initial default
Shared database, shared schema	Cost-efficient, operationally simple, scalable with controls	Requires rigorous isolation enforcement	Selected
Separate deployment per customer	Strong deployment isolation	Higher operational burden	Customer-hosted edition

3.2 Required isolation layers
The isolation model must not depend on a single authorization check.
Defense-in-depth tenant isolation
01

Identity

Identify the authenticated user and validate the session.


02

Tenant resolution

Resolve the organization from a trusted membership or resource relationship.


03

Authorization

Verify membership, role, restaurant assignment and requested action.


04

Application scope

Pass a server-derived tenant context into the use case.


05

Repository scope

Apply tenant restrictions to every tenant-owned query and write.


06

Database RLS

Use PostgreSQL policies as an additional database boundary.


07

Storage and cache

Enforce tenant-specific object paths and cache namespaces.


08

Audit and monitoring

Record sensitive access and detect suspicious cross-tenant attempts.



All eight layers are part of the target architecture. Some controls, such as RLS, may be implemented incrementally, but the application must not launch without robust application and repository-level tenant enforcement.
3.3 Isolation invariants
1. Every tenant-owned resource has an authoritative organization owner.
2. Every protected request has a validated authorization context.
3. Client-supplied organization IDs are selectors, not proof of access.
4. Restaurant access requires organization membership and any applicable branch assignment.
5. Every repository method accessing tenant-owned data receives or derives an authorized tenant scope.
6. No public endpoint can retrieve drafts or unpublished snapshots.
7. Platform staff privileges do not automatically imply unrestricted access to tenant content.
8. Background jobs must carry an explicit tenant context or use a separately authorized system operation.
9. Tenant identifiers must be included in storage and cache isolation keys.
10. Tenant context must be cleared when a database connection is returned to the connection pool.
11. A missing tenant context must fail closed for tenant-protected database operations.
12. Self-hosted installations must retain the same resource ownership and authorization rules.
4. Tenant identity and context resolution
This section defines how the application determines which organization a user is acting within.
4.1 Tenant context
Every authenticated tenant-scoped operation should execute with a validated context.

Proposed context structure:
# shared/application/tenant_context.pyfrom dataclasses import dataclassfrom uuid import UUID@dataclass(frozen=True)class TenantContext:    user_id: UUID    organization_id: UUID    membership_id: UUID    organization_role: str    allowed_restaurant_ids: frozenset[UUID] | None    request_id: str    authentication_method: str



The context must be constructed by trusted backend code after verifying the session and organization membership.

It must not be constructed by directly deserializing a request body such as:
{
  "user_id": "user-a",
  "organization_id": "organization-b",
  "role": "owner"
}


That request is untrusted input. A user cannot assign themselves another tenant or a higher role by modifying client data.
4.2 Tenant resolution flow
#chatgpt-mermaid-_r_2m6_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-_r_2m6_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_2m6_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_2m6_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-_r_2m6_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-_r_2m6_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-_r_2m6_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-_r_2m6_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-_r_2m6_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-_r_2m6_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2m6_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2m6_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-_r_2m6_ p{margin:0;}#chatgpt-mermaid-_r_2m6_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ .cluster-label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ .cluster-label span{color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-_r_2m6_ .label text,#chatgpt-mermaid-_r_2m6_ span{fill:rgb(13, 13, 13);color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ .node rect,#chatgpt-mermaid-_r_2m6_ .node circle,#chatgpt-mermaid-_r_2m6_ .node ellipse,#chatgpt-mermaid-_r_2m6_ .node polygon,#chatgpt-mermaid-_r_2m6_ .node path{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ .rough-node .label text,#chatgpt-mermaid-_r_2m6_ .node .label text,#chatgpt-mermaid-_r_2m6_ .image-shape .label,#chatgpt-mermaid-_r_2m6_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-_r_2m6_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ .rough-node .label,#chatgpt-mermaid-_r_2m6_ .node .label,#chatgpt-mermaid-_r_2m6_ .image-shape .label,#chatgpt-mermaid-_r_2m6_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-_r_2m6_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-_r_2m6_ .root .anchor path{fill:rgb(143, 143, 143)!important;stroke-width:0;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2m6_ .arrowheadPath{fill:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2m6_ .edgePath .path{stroke:rgb(143, 143, 143);stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ .flowchart-link{stroke:rgb(143, 143, 143);fill:none;}#chatgpt-mermaid-_r_2m6_ .edgeLabel{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-_r_2m6_ .edgeLabel p{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-_r_2m6_ .edgeLabel rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-_r_2m6_ .labelBkg{background-color:rgba(252, 252, 252, 0.5);}#chatgpt-mermaid-_r_2m6_ .cluster rect{fill:rgb(243, 243, 243);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ .cluster text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ .cluster span{color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(243, 243, 243);border:1px solid rgba(0, 0, 0, 0.1);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-_r_2m6_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2m6_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-_r_2m6_ .icon-shape,#chatgpt-mermaid-_r_2m6_ .image-shape{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-_r_2m6_ .icon-shape p,#chatgpt-mermaid-_r_2m6_ .image-shape p{background-color:rgb(252, 252, 252);padding:2px;}#chatgpt-mermaid-_r_2m6_ .icon-shape .label rect,#chatgpt-mermaid-_r_2m6_ .image-shape .label rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-_r_2m6_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-_r_2m6_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-_r_2m6_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].node rect,#chatgpt-mermaid-_r_2m6_ [data-look="neo"].cluster rect,#chatgpt-mermaid-_r_2m6_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-_r_2m6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-_r_2m6_-gradient);stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-_r_2m6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-_r_2m6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2m6_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-_r_2m6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2m6_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(0, 79, 153);}#chatgpt-mermaid-_r_2m6_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(0, 79, 153);}#chatgpt-mermaid-_r_2m6_ .node tspan[font-weight="normal"],#chatgpt-mermaid-_r_2m6_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-_r_2m6_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ .node rect,#chatgpt-mermaid-_r_2m6_ .node circle,#chatgpt-mermaid-_r_2m6_ .node ellipse,#chatgpt-mermaid-_r_2m6_ .node polygon,#chatgpt-mermaid-_r_2m6_ .node path{fill:rgb(229, 243, 255);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-_r_2m6_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-_r_2m6_ .mermaid-decision .label-container{fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-dasharray:2,2;}#chatgpt-mermaid-_r_2m6_ .edgePaths .flowchart-link{stroke:rgb(143, 143, 143);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-_r_2m6_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2m6_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Incoming requestValidate sessionAuthenticated?401 UnauthorizedResolve requested resource ororganizationLoad membership from trusteddataActive membership?403 or controlled 404Check organization roleCheck restaurant assignmentAuthorized?Construct TenantContextExecute application use caseScoped repository and RLSNoYesNoYesNoYes





4.3 Selecting an organization
A user may belong to multiple organizations. The application therefore needs an explicit organization-selection mechanism.

Recommended behavior:
1. User authenticates.
2. Backend obtains the user's active memberships.
3. User selects an organization or accesses a resource with an unambiguous organization relationship.
4. Backend validates that membership.
5. Backend constructs the tenant context.
6. The context is used for the duration of the authorized operation.
An organization ID in a URL such as /organizations/{organization_id}/menus can be used to select the requested organization, but the backend must independently verify that the user is an active member with sufficient permissions.
4.4 Trusted tenant context propagation
The tenant context should flow through the application as an explicit parameter.
# modules/menus/application/commands/create_menu.pyfrom dataclasses import dataclassfrom uuid import UUIDfrom app.shared.application.tenant_context import TenantContext@dataclass(frozen=True)class CreateMenuCommand:    name: str    restaurant_id: UUIDclass CreateMenuUseCase:    def __init__(self, repository, restaurant_reader):        self.repository = repository        self.restaurant_reader = restaurant_reader    def execute(        self,        command: CreateMenuCommand,        context: TenantContext,    ):        restaurant = self.restaurant_reader.get_for_tenant(            restaurant_id=command.restaurant_id,            organization_id=context.organization_id,        )        if restaurant is None:            raise ValueError("Restaurant not found")        menu = self.repository.create(            organization_id=context.organization_id,            restaurant_id=restaurant.id,



The exact authorization and error-handling behavior will be finalized in ARC-07. This illustrates the important rule: the organization ID comes from the trusted context, not the command.
4.5 Tenant context lifecycle
The context must have a clearly defined lifecycle:
- Created after authentication and membership verification.
- Passed to the application use case.
- Applied to the database transaction.
- Included in relevant audit and correlation metadata.
- Discarded after the request or job completes.
Do not store the active tenant in a global mutable variable. Concurrent requests from different organizations must never overwrite each other's context.

5. Organization membership and authorization architecture
Authentication answers who is making the request? Authorization answers what may that person do, and on which resource?

A valid login is not sufficient to access a restaurant.
5.1 Role model
The following organization-level roles are proposed.
Role	Purpose	Typical capabilities
Organization Owner	Owns the tenant	Full organization and restaurant administration
Organization Admin	Manages organization operations	Members, branches, configuration
Restaurant Manager	Manages assigned restaurants	Menu, pricing, publication
Menu Editor	Edits assigned menus	Content and design editing
Viewer	Read-only access	View permitted dashboard resources

Platform roles are separate:
Platform role	Purpose
Platform Owner	Overall platform administration
Platform Staff	Limited operational administration
Support Operator	Authorized support workflows, if introduced

Do not treat the roles as a single universal hierarchy. Platform permissions and organization permissions are separate security domains.
5.2 Role and permission matrix
The following is the proposed starting permission model. The final matrix must be reviewed against the actual business requirements.
Permission	Owner	Org Admin	Manager	Editor	Viewer
View organization	✓	✓	—	—	—
Manage organization settings	✓	✓	—	—	—
Manage memberships	✓	✓*	—	—	—
Create restaurant	✓	✓	—	—	—
View assigned restaurant	✓	✓	✓	✓	✓
Edit restaurant profile	✓	✓	✓	—	—
Manage menu content	✓	✓	✓	✓	—
Edit themes/layouts	✓	✓	✓	✓	—
Publish menu	✓	✓	✓**	—	—
Manage subscription	✓	✓*	—	—	—
Delete organization	✓	—	—	—	—

* Permission depends on explicit delegated policy. Organization admins should not automatically be allowed to transfer ownership or perform irreversible owner-only operations.

** Restaurant managers can publish only where the owner/admin has granted publication permission.
5.3 Restaurant-level assignment
Organization membership may provide access to the organization without granting access to every restaurant.

For example:
- A restaurant manager may manage Branch A only.
- A menu editor may edit Branch A's menu but not Branch B's.
- An organization owner may access all branches.
- A viewer may have access to a selected set of restaurants.
The system should support two concepts:
1. Organization-level role.
2. Optional restaurant-level assignment or permission restriction.
The authorization policy must combine them.
5.4 Authorization decision model
For a protected operation:
\[
\text{Allow} =
A \land M \land R \land P \land S
\]

Where:
- \(A\): valid authenticated identity.
- \(M\): active organization membership.
- \(R\): sufficient organization role.
- \(P\): permission for the requested action.
- \(S\): resource scope permits access to the requested restaurant or resource.
For example, a Menu Editor may satisfy membership and role checks but still fail a menu.publish permission check.
5.5 Permission vocabulary
Use stable permission identifiers rather than scattered role-name comparisons.
# shared/domain/permissions.pyfrom enum import StrEnumclass Permission(StrEnum):    ORGANIZATION_READ = "organization.read"    ORGANIZATION_UPDATE = "organization.update"    MEMBER_INVITE = "organization.member.invite"    MEMBER_REMOVE = "organization.member.remove"    RESTAURANT_CREATE = "restaurant.create"    RESTAURANT_READ = "restaurant.read"    RESTAURANT_UPDATE = "restaurant.update"    MENU_CREATE = "menu.create"    MENU_READ = "menu.read"    MENU_UPDATE = "menu.update"    MENU_DELETE = "menu.delete"    MENU_PUBLISH = "menu.publish"    MENU_ROLLBACK = "menu.rollback"    THEME_UPDATE = "theme.update"    LAYOUT_UPDATE = "layout.update"    SUBSCRIPTION_READ = "subscription.read"    SUBSCRIPTION_MANAGE = "subscription.manage"



The permission vocabulary should be centralized and version-controlled. Role-to-permission assignments should be defined in an explicit policy rather than hardcoded independently in every API route.
5.6 Authorization policy example
# shared/application/authorization.pyfrom dataclasses import dataclassfrom app.shared.application.tenant_context import TenantContextfrom app.shared.domain.permissions import Permission@dataclass(frozen=True)class AuthorizationPolicy:    role_permissions: dict[str, frozenset[Permission]]    def require(        self,        context: TenantContext,        permission: Permission,    ) -> None:        allowed = self.role_permissions.get(            context.organization_role,            frozenset(),        )        if permission not in allowed:            raise PermissionError("Permission denied")



This example shows role-based authorization only. Production authorization must also enforce resource-level scope, membership status, restaurant assignments, delegated permissions and relevant licensing restrictions.
5.7 Platform administration separation
Platform operators require their own authorization mechanism.

Rules:
1. A platform role must not automatically become an organization owner.
2. A tenant user role must not grant platform access.
3. Support access should be separately granted, purpose-limited and time-limited where feasible.
4. Sensitive support access must require an auditable reason.
5. Support access must be restricted to the specific customer/resource required.
6. Privileged operations should be logged and monitored.
7. Platform administration must not silently bypass normal business authorization.
Proposed future capability: A support-access workflow with explicit customer authorization, scoped access, expiry and an audit record. It should not be implemented as an unrestricted is_superuser shortcut.

6. Resource ownership architecture
Tenant isolation is only reliable if resource ownership is consistently defined.
6.1 Ownership model
Resource	Authoritative owner	Scope
User account	MOD-01	Global identity
Organization	MOD-02	Tenant
Membership	MOD-02	Tenant/user relationship
Restaurant	MOD-03	Tenant
Restaurant settings	MOD-03	Tenant + restaurant
Menu	MOD-04	Tenant + restaurant
Category	MOD-05	Tenant + restaurant + menu
Food item	MOD-06	Tenant + restaurant
Price	MOD-07	Tenant + restaurant + item
Theme definition	MOD-08	Platform/shared or tenant-owned, depending on type
Restaurant theme selection	MOD-03 / configuration contract	Tenant + restaurant
Layout definition	MOD-09	Platform/shared or tenant-owned
Component definition	MOD-10	Platform registry or approved extension
Editor draft	MOD-12	Tenant + restaurant + user/session
Published version	MOD-13	Tenant + restaurant + menu
Media asset	MOD-14	Tenant + restaurant
Subscription	MOD-15	Tenant
License	MOD-15	Tenant/deployment
Analytics data	MOD-16	Tenant-scoped or aggregated

6.2 Platform-owned versus tenant-owned data
Not every record needs an organization ID.

Platform-owned data examples:
- Built-in theme presets.
- Built-in component definitions.
- Supported layout definitions.
- Global application settings.
- Currency metadata.
- Shared product documentation.
Tenant-owned data examples:
- Restaurant profiles.
- Menu content.
- Restaurant-specific themes.
- Restaurant design configuration.
- Drafts and publications.
- Media assets.
- Organization memberships.
- Subscription records.
The architecture must explicitly identify the owner of each resource rather than automatically adding a tenant ID to every table.
6.3 Ownership rules
- Tenant-owned data must have an authoritative organization relationship.
- Child records must not be accessible through a parent ID alone.
- The server must verify the complete ownership chain.
- The client must not be allowed to reassign resource ownership by changing an organization or restaurant ID.
- Ownership transfers require an explicit authorized workflow.
- Platform-owned shared definitions must be read-only to tenant users unless an approved extension model exists.
6.4 Ownership chain
A typical menu resource is associated with:
Organization
   └── Restaurant
         └── Menu
               └── Category
                     └── Food Item
                           └── Price / Availability


The ownership chain should be validated when a resource is created, reassigned, published or accessed.

A food-item ID from another restaurant must not become accessible simply because the caller knows its UUID.

7. Backend tenant enforcement
7.1 Required backend request lifecycle
Application Use CasePostgreSQLAuthorizationIdentityFastAPIClientApplication Use CasePostgreSQLAuthorizationIdentityFastAPIClient#chatgpt-mermaid-_r_2n3_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-_r_2n3_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_2n3_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_2n3_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-_r_2n3_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-_r_2n3_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-_r_2n3_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-_r_2n3_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-_r_2n3_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-_r_2n3_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-_r_2n3_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-_r_2n3_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-_r_2n3_ p{margin:0;}#chatgpt-mermaid-_r_2n3_ .actor{stroke:rgb(83, 154, 248);fill:rgb(222, 234, 251);stroke-width:1;}#chatgpt-mermaid-_r_2n3_ rect.actor.outer-path[data-look="neo"]{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2n3_ rect.note[data-look="neo"]{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2n3_ text.actor>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-_r_2n3_ .actor-line{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ .innerArc{stroke-width:1.5;stroke-dasharray:none;}#chatgpt-mermaid-_r_2n3_ .messageLine0{stroke-width:1.5;stroke-dasharray:none;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ .messageLine1{stroke-width:1.5;stroke-dasharray:2,2;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ [id$="-arrowhead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ .sequenceNumber{fill:#707070;}#chatgpt-mermaid-_r_2n3_ [id$="-sequencenumber"]{fill:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ [id$="-crosshead"] path{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_2n3_ .messageText{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-_r_2n3_ .labelBox{stroke:rgba(0, 0, 0, 0.1);fill:rgb(252, 252, 252);filter:none;}#chatgpt-mermaid-_r_2n3_ .labelText,#chatgpt-mermaid-_r_2n3_ .labelText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-_r_2n3_ .loopText,#chatgpt-mermaid-_r_2n3_ .loopText>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-_r_2n3_ .sectionTitle,#chatgpt-mermaid-_r_2n3_ .sectionTitle>tspan{fill:rgb(13, 13, 13);stroke:none;}#chatgpt-mermaid-_r_2n3_ .loopLine{stroke-width:2px;stroke-dasharray:2,2;stroke:rgba(0, 0, 0, 0.1);fill:rgba(0, 0, 0, 0.1);}#chatgpt-mermaid-_r_2n3_ .note{stroke:rgb(107, 198, 127);fill:rgb(243, 243, 243);}#chatgpt-mermaid-_r_2n3_ .noteText,#chatgpt-mermaid-_r_2n3_ .noteText>tspan{fill:rgb(13, 13, 13);stroke:none;font-weight:normal;}#chatgpt-mermaid-_r_2n3_ .activation0{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-_r_2n3_ .activation1{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-_r_2n3_ .activation2{fill:rgb(243, 243, 243);stroke:hsl(0, 0%, 85.2941176471%);}#chatgpt-mermaid-_r_2n3_ .actorPopupMenu{position:absolute;}#chatgpt-mermaid-_r_2n3_ .actorPopupMenuPanel{position:absolute;fill:rgb(222, 234, 251);box-shadow:0px 8px 16px 0px rgba(0,0,0,0.2);filter:drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));}#chatgpt-mermaid-_r_2n3_ .actor-man circle,#chatgpt-mermaid-_r_2n3_ line{fill:rgb(222, 234, 251);stroke-width:2px;}#chatgpt-mermaid-_r_2n3_ g rect.rect{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));stroke:rgb(83, 154, 248);}#chatgpt-mermaid-_r_2n3_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].node rect,#chatgpt-mermaid-_r_2n3_ [data-look="neo"].cluster rect,#chatgpt-mermaid-_r_2n3_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-_r_2n3_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-_r_2n3_-gradient);stroke-width:1px;}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-_r_2n3_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-_r_2n3_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2n3_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-_r_2n3_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_2n3_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Protected requestValidate sessionUser identityResolve membership and scopeVerify active membershipMembership resultTrusted TenantContextBegin transaction + set tenant contextExecute with TenantContextTenant-scoped repository operationsAuthorized recordsResultCommit / rollbackResponse





7.2 FastAPI dependency
Illustrative request dependency:
# api/dependencies/tenant.pyfrom fastapi import Depends, HTTPExceptionfrom uuid import UUIDfrom app.shared.application.tenant_context import TenantContextdef get_tenant_context(    organization_id: UUID,    current_user=Depends(get_current_user),    membership_service=Depends(get_membership_service),) -> TenantContext:    membership = membership_service.get_active_membership(        user_id=current_user.id,        organization_id=organization_id,    )    if membership is None:        raise HTTPException(            status_code=404,            detail="Organization not found",        )    return TenantContext(        user_id=current_user.id,        organization_id=membership.organization_id,        membership_id=membership.id,        organization_role=membership.role,        allowed_restaurant_ids=frozenset(            membership.allowed_restaurant_ids        ) if membership.allowed_restaurant_ids is not None else None,        request_id=current_request_id(),        authentication_method="session",    )



The example assumes the application has a verified user session, a membership service and a trusted request ID provider. Those helpers must be implemented according to ARC-03 and ARC-07.

Important: A route parameter can select the requested organization, but the dependency resolves and verifies the actual membership. The route parameter never directly creates the tenant context.
7.3 Repository enforcement
Every tenant-owned repository should make tenant scope explicit.
# modules/menus/infrastructure/repositories/sql_menu_repository.pyfrom uuid import UUIDfrom sqlalchemy import selectclass SqlMenuRepository:    def __init__(self, session):        self.session = session    def get_for_tenant(        self,        menu_id: UUID,        organization_id: UUID,    ):        statement = select(MenuModel).where(            MenuModel.id == menu_id,            MenuModel.organization_id == organization_id,        )        return self.session.scalar(statement)    def list_for_tenant(        self,        organization_id: UUID,        restaurant_id: UUID,    ):        statement = select(MenuModel).where(            MenuModel.organization_id == organization_id,            MenuModel.restaurant_id == restaurant_id,        )        return list(self.session.scalars(statement).all())



Required repository conventions:
- No tenant-scoped get_by_id() method without a scope argument.
- No tenant-scoped list_all() method available to normal tenant application services.
- No update or delete without an ownership condition.
- No bulk operation without a tenant restriction.
- No use of user-supplied ownership values in place of the trusted context.
- No repository method may silently default to an unrestricted scope.
For especially sensitive operations, require the complete organization and restaurant scope rather than organization scope alone.
7.4 Safe update pattern
from sqlalchemy import updatedef update_menu_name(    session,    menu_id,    organization_id,    restaurant_id,    new_name,):    statement = (        update(MenuModel)        .where(            MenuModel.id == menu_id,            MenuModel.organization_id == organization_id,            MenuModel.restaurant_id == restaurant_id,        )        .values(name=new_name)        .returning(MenuModel.id)    )    return session.scalar(statement)



The caller must still validate permission and business rules. Tenant filtering is not a substitute for application authorization.

8. PostgreSQL Row-Level Security architecture
8.1 Purpose
PostgreSQL Row-Level Security (RLS) provides a database-enforced layer of tenant isolation.

It helps protect against:
- Missing tenant filters in repository queries.
- Accidental unscoped SQL.
- Certain implementation mistakes in new modules.
- Unauthorized data access through database paths that use the restricted runtime role.
RLS is defense in depth. It does not replace authentication, authorization or repository-level filtering.
8.2 RLS strategy
Use a transaction-scoped PostgreSQL setting to pass the trusted tenant context to database policies.

For example:
SELECT set_config(
    'app.current_organization_id',
    '00000000-0000-0000-0000-000000000001',
    true
);


The third argument true makes the setting local to the current transaction.

This is essential when connections are pooled: a tenant context must not leak into the next transaction using the same connection.
8.3 Example RLS policy
Illustrative SQL:
ALTER TABLE menus ENABLE ROW LEVEL SECURITY;

ALTER TABLE menus FORCE ROW LEVEL SECURITY;

CREATE POLICY menus_tenant_isolation
ON menus
USING (
    organization_id =
    NULLIF(
        current_setting(
            'app.current_organization_id',
            true
        ),
        ''
    )::uuid
)
WITH CHECK (
    organization_id =
    NULLIF(
        current_setting(
            'app.current_organization_id',
            true
        ),
        ''
    )::uuid
);


The policy ensures:
- Reads are restricted to the current organization.
- Updates and deletes are restricted to rows visible under the policy.
- Inserts and updated ownership values must satisfy the policy.
A missing or empty tenant setting produces no matching organization and therefore denies access.
8.4 Transaction setup in SQLAlchemy
# infrastructure/database/tenant_session.pyfrom uuid import UUIDfrom sqlalchemy import textfrom sqlalchemy.orm import Sessiondef apply_tenant_context(    session: Session,    organization_id: UUID,) -> None:    session.execute(        text(            """            SELECT set_config(                'app.current_organization_id',                :organization_id,                true            )            """        ),        {            "organization_id": str(organization_id)        },    )



Usage:
def execute_tenant_operation(    session: Session,    context: TenantContext,    use_case,    command,):    with session.begin():        apply_tenant_context(            session,            context.organization_id,        )        return use_case.execute(            command,            context,        )



The transaction must begin before the tenant setting is applied, and all protected queries must use the same transaction-bound session.

Do not set the tenant context in a long-lived pooled connection outside a transaction.
8.5 Database role requirements
This is a critical deployment requirement.

The normal application database role must:
- Not be a PostgreSQL superuser.
- Not have BYPASSRLS.
- Not own the protected tables.
- Not have privileges to disable RLS.
- Have only required database privileges.
- Use the protected tables through RLS policies.
Use a separate migration/administrative role for schema changes.

FORCE ROW LEVEL SECURITY is important because table owners normally bypass RLS. However, superusers and roles with BYPASSRLS remain privileged; they must never be used as the normal application connection.
8.6 RLS coverage
RLS should be applied to all tenant-owned tables, including:
- Organizations where tenant-level row visibility is appropriate.
- Memberships.
- Restaurants.
- Restaurant settings.
- Menus.
- Categories.
- Food items.
- Prices.
- Availability rules.
- Restaurant design configurations.
- Editor drafts.
- Publications.
- Published versions.
- Media metadata.
- Subscriptions and licenses.
- Tenant analytics records.
Shared platform-owned reference data should use separate policies or read-only access patterns.
8.7 Nested resource integrity
RLS on a menu table does not automatically guarantee that every category, item and price has a valid parent in the same organization.

ARC-06 must define relational constraints that prevent invalid cross-tenant relationships.

For example, a category belonging to Organization A must not be attached to a menu belonging to Organization B.

Use tenant-aware composite keys or equivalent relational constraints where appropriate.
8.8 RLS limitations and threat model
RLS does not protect against every possible database threat.
- A compromised application process with unrestricted credentials can bypass application protections.
- A database superuser can bypass RLS.
- Incorrectly set tenant context can expose the wrong scope.
- Unsafe SECURITY DEFINER functions can create bypass paths.
- A tenant setting is a trusted application assertion, not a cryptographic proof of identity.
Therefore, the design must combine application authorization, scoped repositories, database role restrictions, RLS, auditability and operational controls.

9. Tenant-aware database architecture
ARC-06 will define the complete schema, but ARC-05 establishes the tenancy requirements that schema must satisfy.
9.1 Tenant identifier strategy
Use UUID identifiers for organization and resource identities.

Every tenant-owned entity should have an authoritative organization relationship.

Proposed logical fields:
Organization
    id

Restaurant
    id
    organization_id

Menu
    id
    organization_id
    restaurant_id

Category
    id
    organization_id
    restaurant_id
    menu_id

FoodItem
    id
    organization_id
    restaurant_id
    category_id

Price
    id
    organization_id
    restaurant_id
    food_item_id

PublishedVersion
    id
    organization_id
    restaurant_id
    menu_id


These are logical ownership fields, not the final schema.
9.2 Tenant-aware relational integrity
Consider a category linked to a menu.

A weak schema might only enforce:
FOREIGN KEY (menu_id)
REFERENCES menus(id)


This verifies that the menu exists, but not necessarily that the category's organization matches the menu's organization.

A tenant-aware relationship can use:
FOREIGN KEY (organization_id, menu_id)
REFERENCES menus(organization_id, id)


The referenced columns must have an appropriate unique constraint, such as:
UNIQUE (organization_id, id)


The final design must apply this consistently to tenant-owned parent-child relationships.
9.3 Database indexing
Proposed tenant-aware indexing strategy:
CREATE INDEX idx_restaurants_org
ON restaurants (organization_id);

CREATE INDEX idx_menus_org_restaurant
ON menus (organization_id, restaurant_id);

CREATE INDEX idx_categories_org_menu
ON categories (organization_id, menu_id);

CREATE INDEX idx_food_items_org_restaurant
ON food_items (organization_id, restaurant_id);

CREATE INDEX idx_publications_org_menu
ON publications (organization_id, menu_id);


These are representative indexes. ARC-06 will determine actual composite constraints and index ordering based on access patterns and query plans.
9.4 Ownership mutation restrictions
Normal users must not be able to change organization_id or parent ownership fields through ordinary update endpoints.

Ownership changes must be separate, explicit operations with:
- Permission checks.
- Parent relationship validation.
- Transactional behavior.
- Audit events.
- Impact analysis.
- Defined rollback or recovery behavior.

10. Tenant-aware file and media storage
Media is a common cross-tenant leakage path because object storage permissions can be less restrictive than database permissions.
10.1 Object-key architecture
Use organization-scoped object keys.

Example:
media/
└── organizations/
    ├── {organization_id}/
    │   ├── restaurants/
    │   │   ├── {restaurant_id}/
    │   │   │   ├── logos/
    │   │   │   ├── food-items/
    │   │   │   ├── banners/
    │   │   │   └── generated/


The object key must be generated by trusted backend code. Never allow a client to submit an arbitrary storage path and use it directly.
10.2 Upload workflow
1. Authenticate user.
2. Resolve tenant context.
3. Validate organization membership and restaurant access.
4. Validate upload permission.
5. Check allowed MIME type, actual file signature and size.
6. Generate a unique asset ID.
7. Generate a tenant-scoped object key.
8. Upload through the storage adapter.
9. Persist asset metadata with organization and restaurant ownership.
10. Record audit metadata.
11. Return a safe asset reference.
10.3 Private media access
For private media:
- Verify resource ownership before generating a signed URL.
- Use short-lived signed URLs.
- Do not expose bucket credentials or internal storage endpoints.
- Never use a public URL as proof of authorization.
- Prevent object-key traversal and arbitrary bucket access.
- Apply deletion/reference checks.
10.4 Public media exception
A restaurant may intentionally publish a food image or logo publicly.

Public visibility must be explicitly derived from a published menu or approved public asset policy, not merely from the fact that an object exists.

Public delivery should use controlled asset URLs or a CDN path that exposes only published content.
10.5 Storage isolation tests
- Tenant A cannot request a private asset belonging to Tenant B.
- Tenant A cannot generate a signed URL for Tenant B's object.
- A modified object key cannot bypass authorization.
- An unpublished asset is not publicly accessible.
- A deleted asset cannot be retrieved through a stale private URL after its access expiry.
- A public asset is exposed only when explicitly authorized for publication.
11. Tenant-aware cache architecture
Caching must preserve the same isolation guarantees as the database.
11.1 Cache key design
Every tenant-specific cache entry must include the tenant identity and the relevant resource scope.

Examples:
tenant:{organization_id}:restaurant:{restaurant_id}:profile
tenant:{organization_id}:restaurant:{restaurant_id}:settings
tenant:{organization_id}:restaurant:{restaurant_id}:menu:{menu_id}
tenant:{organization_id}:restaurant:{restaurant_id}:publication:{version_id}


Avoid generic keys such as:
menu:{menu_id}
restaurant:{slug}
user:dashboard


unless the data is deliberately public, the key is globally unique, and the associated authorization and invalidation rules are explicitly documented.
11.2 Cache policy
Data type	Recommended cache strategy
User session	Secure session-specific key
Membership	Short-lived cache with revocation/invalidation
Restaurant settings	Tenant-scoped cache
Menu drafts	Tenant-scoped, private
Editor state	User/session and tenant-scoped
Published menu	Publication/version-aware cache
Public restaurant menu	Public route key and active version
Subscription entitlements	Tenant-scoped with timely invalidation
Platform reference data	Shared read-only cache

11.3 Cache invalidation
A publication change must invalidate or supersede relevant public-menu cache entries.

Membership removal, role changes and restaurant assignment changes must invalidate any cached authorization state within the defined revocation window.

Security requirement: Authorization must not rely on a cache entry whose validity can outlive the intended access-revocation policy.
11.4 Redis optionality
As established in ARC-01 and ARC-03, Redis is optional in the initial application architecture.

Therefore:
- Core tenant isolation must work without Redis.
- In-memory caches must never be shared across requests without tenant-safe keys and concurrency-safe behavior.
- Redis failure must not cause a fallback to unscoped data access.
- Cache misses must return to the authoritative data layer with tenant filters and authorization intact.

12. Public menu and tenant boundary
The public menu is a deliberate exception to the requirement for authenticated organization membership. A customer must be able to browse a restaurant's published menu without creating an account.

This must be handled as a separate public-access policy, not as a relaxation of tenant isolation.
12.1 Public access boundary
Private tenant area
Authentication required
- Draft menus
- Editor sessions
- Private settings
- Member records
- Subscriptions
- Unpublished media
- Publication history


Public delivery area
Public read
- Published restaurant profile
- Published menu content
- Approved food images
- Public prices
- Public availability
- Public design configuration



Public delivery is restricted to explicitly published data. It does not expose the underlying tenant's private database or management interfaces.
12.2 Public menu resolution
Recommended route:
/r/{restaurant_slug}/{menu_slug}


Resolution sequence:
1. Resolve restaurant slug.
2. Verify that the restaurant is active and publicly accessible.
3. Resolve the requested menu.
4. Verify that the menu has an active publication.
5. Retrieve the active immutable snapshot.
6. Resolve public media references.
7. Return only the approved public representation.
The public route must never fetch a draft and then attempt to remove private fields from the response.

It should retrieve the published representation directly.
12.3 Public API design
Conceptual routes:
GET /api/v1/public/restaurants/{restaurant_slug}
GET /api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}
GET /api/v1/public/publications/{publication_id}


The final route structure is reserved for ARC-07.
12.4 Public API restrictions
- No organization membership records.
- No private restaurant settings.
- No draft menu data.
- No editor state.
- No private asset metadata.
- No subscription or licensing information.
- No internal IDs unless required by a deliberate public contract.
- No unrestricted query filters allowing enumeration of tenant resources.
- No public access to publication history unless intentionally designed as a feature.
12.5 Public visibility and unpublished changes
A restaurant owner may edit a draft without changing what customers currently see.

The public menu must continue using the active published version until a new version is successfully published.

This separates:
- Private editing state.
- Publication candidate state.
- Active public state.

13. Background jobs and asynchronous processing
Tenant isolation must continue outside HTTP requests.

Examples of asynchronous operations:
- Image processing.
- Email notifications.
- Scheduled availability changes.
- Analytics aggregation.
- Publication-related cache invalidation.
- Subscription entitlement updates.
- License renewal and expiry checks.
13.1 Tenant context in background jobs
Every tenant-specific job must include sufficient scope to re-establish authorization.

Example job envelope:
from dataclasses import dataclassfrom uuid import UUID@dataclass(frozen=True)class TenantJobContext:    organization_id: UUID    restaurant_id: UUID | None    initiating_user_id: UUID | None    correlation_id: str    job_id: str    purpose: str



The worker must not trust a queued organization ID without validating that the referenced resources belong to that organization.
13.2 Background worker execution
1. Receive job.
2. Validate job schema.
3. Validate job type and permitted purpose.
4. Resolve the target resource.
5. Verify tenant ownership.
6. Start a new database transaction.
7. Apply transaction-scoped tenant context.
8. Execute the job.
9. Persist outcome.
10. Record audit/operational metadata.
11. Clear transaction context by committing or rolling back.
13.3 System jobs
Some jobs legitimately operate across all tenants, such as:
- Subscription expiry processing.
- Global platform health checks.
- Scheduled maintenance.
- Aggregate billing reconciliation.
These must use a separate system-job authorization path.

Do not represent a system job as an ordinary tenant request with a magic organization ID.

System jobs should:
- Use a separate, limited database role or explicitly authorized execution mechanism.
- Have a documented purpose and scope.
- Avoid unrestricted use of normal tenant repositories.
- Log each tenant processed.
- Support bounded batches and safe retries.
- Never inherit a previous worker job's tenant context.
13.4 Worker isolation test
A worker processing a Tenant A job must not:
- Read Tenant B resources.
- Write to Tenant B resources.
- Generate signed URLs for Tenant B.
- Reuse Tenant A context for a subsequent Tenant B job.
- Process a forged or inconsistent organization/resource relationship.

14. Tenant lifecycle architecture
Tenant lifecycle must cover the complete commercial and operational lifetime of an organization.
14.1 Lifecycle states
Provisioning
Initial

Active
Suspended
Temporary access restriction

Offboarding
Controlled termination process


Deactivated / Deleted
Subject to retention, legal and recovery policies

These are conceptual states. Suspension, deletion and subscription expiration are distinct concepts and should not be collapsed into one field.
14.2 Provisioning workflow
Actions:
1. Create organization.
2. Assign initial owner.
3. Create membership.
4. Establish tenant settings.
5. Create initial restaurant if requested.
6. Establish default theme and menu configuration.
7. Initialize subscription/trial state if applicable.
8. Record tenant provisioning event.
9. Verify successful isolation.
10. Mark tenant active.
Provisioning should be idempotent or have reliable recovery behavior so a retry does not create duplicate organizations.
14.3 Suspension workflow
A suspended organization should have an explicit policy describing:
- Whether organization owners may sign in.
- Whether menu editing is blocked.
- Whether publication is blocked.
- Whether the existing public menu remains accessible.
- Whether media remains accessible.
- Whether subscription and licensing data remain readable.
- Whether support access is available.
Proposed default: Suspension blocks tenant management operations and new publications. Existing published public menus may remain available during a documented grace period or until the owner chooses to disable public access. The final commercial policy must be confirmed before implementation.
14.4 Offboarding workflow
1. Verify owner authorization or authorized platform process.
2. Confirm offboarding intent.
3. Display impact and retention information.
4. Block new management activity.
5. Decide public-menu shutdown behavior.
6. Preserve required audit records.
7. Apply data export or retention policy.
8. Process media retention/deletion.
9. Revoke sessions and invitations.
10. Revoke relevant licenses or entitlements.
11. Execute deletion or anonymization under the approved policy.
12. Record completion and evidence.
Do not immediately hard-delete organization records and all associated data without first defining retention, backup and recovery requirements.
14.5 Data deletion and restoration
- Tenant deletion must be scoped to that tenant.
- Cascading deletion must not affect another tenant.
- Restoring a backup must preserve organization ownership and isolation.
- A tenant restore must not unintentionally overwrite unrelated tenants.
- Backup access must be restricted to authorized operations personnel.
- Retention and deletion policy must be documented and reviewed for applicable law.
Detailed backup, recovery and deployment controls belong to ARC-11 and ARC-12.

15. Tenant-aware application and repository structure
The following extends the ARC-03 and ARC-04 structures.
backend/
└── app/
    ├── shared/
    │   ├── application/
    │   │   ├── tenant_context.py
    │   │   ├── tenant_resolver.py
    │   │   └── authorization.py
    │   ├── domain/
    │   │   ├── permissions.py
    │   │   └── tenant_exceptions.py
    │   └── infrastructure/
    │       └── tenant_database.py
    │
    ├── modules/
    │   ├── identity/
    │   ├── organizations/
    │   ├── memberships/
    │   ├── restaurants/
    │   ├── menus/
    │   ├── categories/
    │   ├── food_items/
    │   ├── pricing/
    │   ├── themes/
    │   ├── layouts/
    │   ├── components/
    │   ├── editor/
    │   ├── publishing/
    │   ├── media/
    │   ├── licensing/
    │   └── analytics/
    │
    ├── infrastructure/
    │   ├── database/
    │   │   ├── session.py
    │   │   ├── tenant_session.py
    │   │   ├── rls.py
    │   │   └── roles.py
    │   ├── storage/
    │   │   └── tenant_storage.py
    │   ├── cache/
    │   │   └── tenant_cache.py
    │   └── workers/
    │       └── tenant_job_context.py
    │
    └── tests/
        ├── tenant_isolation/
        ├── authorization/
        ├── rls/
        ├── storage/
        └── integration/


The memberships directory is shown as a possible implementation package within MOD-02, not necessarily a new independent business module.
15.1 Required shared files
File	Responsibility
tenant_context.py	Immutable trusted request/job context
tenant_resolver.py	Resolve and validate active membership
authorization.py	Permission and resource-scope checks
permissions.py	Stable permission identifiers
tenant_exceptions.py	Controlled tenant authorization errors
tenant_session.py	Apply tenant context within DB transactions
rls.py	Database RLS policy management/testing helpers
tenant_storage.py	Tenant-safe object key generation
tenant_cache.py	Tenant-safe cache-key construction
tenant_job_context.py	Tenant scope for asynchronous operations

16. Configuration and deployment requirements
16.1 Environment configuration
Tenant isolation configuration must be centralized and validated at application startup.

Illustrative environment variables:
APP_ENV=development

DATABASE_URL=postgresql+psycopg://app_runtime:local_password@localhost:5432/modularmenu

DATABASE_MIGRATION_URL=postgresql+psycopg://migration_user:local_password@localhost:5432/modularmenu

TENANT_RLS_ENABLED=true
TENANT_CONTEXT_SETTING=app.current_organization_id

TENANT_CACHE_PREFIX=tenant
TENANT_STORAGE_PREFIX=organizations

ALLOW_PLATFORM_SUPPORT_ACCESS=false


These values are examples for local development. Real credentials must come from a secrets mechanism, not committed environment files.
16.2 Configuration rules
- Production SaaS must not silently disable RLS.
- The runtime database role must be checked against the required privileges.
- Migration and runtime database credentials must be separate.
- Missing tenant context must fail closed.
- Development shortcuts must not be enabled in production.
- Tenant cache and storage namespaces must be validated.
- Customer-hosted deployments must use the same ownership rules.
- Feature flags must not bypass authorization.
16.3 Startup checks
At application startup or deployment verification, validate:
1. Database connection is available.
2. Runtime database role is not a superuser.
3. Runtime database role does not have BYPASSRLS.
4. Runtime role does not own protected tables.
5. RLS is enabled for required tenant-owned tables.
6. Required policies exist.
7. Tenant context configuration is valid.
8. Storage adapter is configured.
9. Cache configuration is valid if Redis is enabled.
A failed critical tenant-isolation check must prevent the application from accepting protected tenant traffic.
16.4 Development and test environments
The development environment should support:
- At least two test organizations.
- Separate users for each organization.
- A user belonging to multiple organizations.
- Multiple restaurants under one organization.
- Restricted branch-level users.
- Cross-tenant attack test fixtures.
- A real PostgreSQL instance for RLS integration tests.
Do not rely solely on SQLite for tenant-isolation validation. SQLite does not reproduce PostgreSQL RLS behavior.

17. API and frontend tenancy requirements
17.1 Frontend tenant selection
The frontend may present:
- Organization selector.
- Restaurant selector.
- Membership-aware navigation.
- Permission-aware controls.
- Active organization indicator.
However, the frontend is not an authorization boundary.

Hiding a button does not prevent a user from calling the endpoint directly.
17.2 Frontend state isolation
When a user switches organizations:
1. Update the active organization context.
2. Clear or invalidate previous organization-specific query caches.
3. Clear selected restaurant and menu state if they do not belong to the new organization.
4. Reload memberships and permissions.
5. Fetch data only within the newly verified scope.
6. Prevent stale requests from populating the new organization view.
17.3 TanStack Query key strategy
Use explicit tenant-aware query keys.
export const menuKeys = {
  all: (organizationId: string) =>
    ["organizations", organizationId, "menus"] as const,

  list: (
    organizationId: string,
    restaurantId: string
  ) =>
    [
      ...menuKeys.all(organizationId),
      "restaurant",
      restaurantId,
    ] as const,

  detail: (
    organizationId: string,
    restaurantId: string,
    menuId: string
  ) =>
    [
      ...menuKeys.list(organizationId, restaurantId),
      "detail",
      menuId,
    ] as const,
};


The organization ID in the query key prevents accidental client-side cache reuse between tenants. It does not authorize a backend request.
17.4 Organization switching
Example state transition:
type ActiveTenantState = {
  organizationId: string | null;
  restaurantId: string | null;
};

function switchOrganization(
  organizationId: string
) {
  // 1. Cancel pending queries from previous tenant.
  // 2. Clear tenant-specific client state.
  // 3. Update active organization.
  // 4. Reload membership and permission context.
  // 5. Fetch authorized resources.
}


Implementation should use the application's actual query-client and state-management lifecycle. Do not simply change a global organization ID while old asynchronous requests remain active.
17.5 Frontend acceptance criteria
- A user cannot view another organization's data by changing the URL.
- Switching organizations does not display stale data.
- An organization switch invalidates old private query data.
- Branch-restricted users see only permitted branches.
- UI permission visibility matches server-side permission decisions.
- Unauthorized operations display a controlled response.
- Public menus remain accessible without tenant login.

18. Tenant audit logging and monitoring
Tenant security requires evidence of sensitive actions.
18.1 Audit events
The following actions should be recorded:
Action	Required audit information
Organization created	Organization ID, creator, timestamp
Member invited	Organization, inviter, invitee reference
Member removed	Organization, actor, affected member
Role changed	Old role, new role, actor
Restaurant created	Organization, restaurant, actor
Restaurant access denied	Requested scope, actor, reason category
Menu accessed or changed	Organization, restaurant, menu, actor
Publication created	Organization, restaurant, menu, version
Publication rollback	Actor, target version, previous version
Media access denied	Asset reference, tenant scope, actor
Subscription changed	Organization, actor/system process
Support access granted	Support identity, tenant, purpose, expiry
Tenant suspended	Organization, reason category, actor

18.2 Audit record structure
Illustrative schema:
from dataclasses import dataclassfrom datetime import datetimefrom uuid import UUID@dataclass(frozen=True)class TenantAuditEvent:    event_id: UUID    organization_id: UUID | None    actor_user_id: UUID | None    action: str    resource_type: str    resource_id: str | None    outcome: str    request_id: str    occurred_at: datetime



For denied requests, the attempted organization ID may be recorded as a requested scope, but it must not be incorrectly represented as the actor's authorized organization.

Avoid logging credentials, session tokens, password reset tokens, signed media URLs or unnecessary personal information.
18.3 Security monitoring
Monitor for:
- Repeated cross-tenant resource access attempts.
- High-volume 403/404 patterns.
- Repeated membership lookup failures.
- Unusual organization switching.
- Abnormal bulk resource enumeration.
- Unexpected RLS denials.
- Privileged database connections from the application.
- Unusual support access.
- Failed or suspicious media access.
- Tenant-scoped cache-key collisions.
Security monitoring and alert thresholds will be finalized in ARC-12.

19. Tenant isolation threat model
The following threat model should be part of the implementation review.
Threat ID	Threat	Attack example	Primary mitigation
ARC05-TH01	IDOR	Change menu ID in request	Ownership and authorization checks
ARC05-TH02	Tenant ID spoofing	Submit another organization ID	Server-derived context
ARC05-TH03	Missing query filter	Unscoped menu listing	Scoped repositories + RLS
ARC05-TH04	Cross-tenant write	Modify another tenant's menu	Scoped update + RLS
ARC05-TH05	Role escalation	Submit owner in request	Server-owned role assignment
ARC05-TH06	Branch access bypass	Access unassigned restaurant	Restaurant-level policy
ARC05-TH07	Cache leakage	Reuse another tenant's cache entry	Tenant-aware keys
ARC05-TH08	Media leakage	Guess another object's key	Authorized signed URLs
ARC05-TH09	Worker context leakage	Reuse prior tenant in worker	Explicit per-job context
ARC05-TH10	RLS bypass	Connect using privileged DB role	Restricted runtime role
ARC05-TH11	Public draft leakage	Request unpublished menu	Published-only delivery
ARC05-TH12	Support abuse	Operator accesses tenant data	Scoped, audited support access
ARC05-TH13	Restore contamination	Restore data into wrong tenant	Tenant-aware recovery procedures
ARC05-TH14	Invitation abuse	Accept another user's invitation	Bound, expiring invitation token
ARC05-TH15	Cross-tenant relationship	Attach foreign item to menu	Composite relational constraints
ARC05-TH16	Concurrent context leakage	Reused connection retains tenant	Transaction-local context
ARC05-TH17	Tenant enumeration	Discover valid organization IDs	Controlled response and rate limiting
ARC05-TH18	Subscription confusion	Use another tenant's entitlement	Tenant-scoped entitlement evaluation

19.1 Priority security requirements
The following are release-blocking:
- TH01 IDOR.
- TH02 tenant ID spoofing.
- TH03 missing query filters.
- TH04 cross-tenant writes.
- TH05 role escalation.
- TH07 cache leakage.
- TH08 media leakage.
- TH09 background worker context leakage.
- TH10 RLS bypass through the normal runtime role.
- TH11 unpublished draft leakage.
- TH15 cross-tenant relational integrity failures.
- TH16 connection context leakage.

20. ARC-05 test strategy
Testing must prove that Tenant A cannot access Tenant B's private resources through every relevant access path.
20.1 Test environment design
Create two organizations and several users:
Tenant A
- Owner A
- Manager A
- Editor A
- Restaurant A1
- Restaurant A2
- Menu A1


Tenant B
- Owner B
- Manager B
- Editor B
- Restaurant B1
- Restaurant B2
- Menu B1



Shared identity test
- User AB belongs to both organizations.
- User AB has different roles in each.
- User AB has limited restaurant assignments.


This fixture verifies both cross-tenant isolation and legitimate multi-tenant membership.
20.2 Detailed test catalogue
Test ID	Area	Test scenario	Expected result
ARC05-T001	Authentication	Anonymous user accesses protected endpoint	401
ARC05-T002	Membership	User accesses own organization	Allowed if role permits
ARC05-T003	Membership	User accesses foreign organization	Denied
ARC05-T004	Membership	Removed member reuses existing session	Denied
ARC05-T005	Tenant resolution	Client submits forged tenant ID	Denied
ARC05-T006	Tenant resolution	User selects a valid second organization	Allowed within its role
ARC05-T007	Organization	User attempts foreign organization update	Denied
ARC05-T008	Organization	User attempts unauthorized ownership transfer	Denied
ARC05-T009	Restaurant	Tenant A requests Restaurant B	Denied
ARC05-T010	Restaurant	Manager accesses unassigned branch	Denied
ARC05-T011	Menu read	Tenant A requests Menu B by UUID	Denied
ARC05-T012	Menu list	Tenant A lists all menus	Only A's menus
ARC05-T013	Menu write	Tenant A updates Menu B	No modification
ARC05-T014	Category	Tenant A accesses Category B	Denied
ARC05-T015	Food item	Tenant A assigns Item B to Menu A	Rejected
ARC05-T016	Pricing	Tenant A updates Price B	Rejected
ARC05-T017	Editor	Tenant A loads Editor Draft B	Denied
ARC05-T018	Publishing	Tenant A publishes Menu B	Denied
ARC05-T019	Publishing	Draft is accessed through public API	Not exposed
ARC05-T020	Publishing	Public request resolves active published snapshot	Allowed
ARC05-T021	Media	Tenant A requests private Asset B	Denied
ARC05-T022	Media	Tenant A requests signed URL for Asset B	Denied
ARC05-T023	Media	Unpublished asset is accessed publicly	Denied
ARC05-T024	Cache	Tenant B requests same resource-shaped key	No A data returned
ARC05-T025	Cache	User switches tenants	Previous tenant data not displayed
ARC05-T026	RLS	Query without tenant setting	No tenant rows
ARC05-T027	RLS	Query under Tenant A context	Only A rows
ARC05-T028	RLS	Tenant A inserts row for Tenant B	Rejected
ARC05-T029	RLS	Tenant A updates Tenant B row	No affected row
ARC05-T030	RLS	Runtime role attempts bypass	Not permitted
ARC05-T031	RLS	Pooled connection reused for Tenant B	Only B data visible
ARC05-T032	RLS	Transaction rolled back after tenant setup	Context does not leak
ARC05-T033	Worker	Tenant A job accesses Tenant B asset	Denied
ARC05-T034	Worker	Consecutive A and B jobs use pooled sessions	No context leakage
ARC05-T035	Worker	Forged organization/resource pair	Job rejected
ARC05-T036	Audit	Cross-tenant access denied	Security event recorded
ARC05-T037	Audit	Role changed	Old/new role recorded
ARC05-T038	Platform admin	Tenant role accesses platform administration	Denied
ARC05-T039	Support	Support operator uses unauthorized scope	Denied and logged
ARC05-T040	Lifecycle	Suspended tenant attempts publishing	Denied
ARC05-T041	Lifecycle	Suspended tenant public menu request	Follows documented suspension policy
ARC05-T042	Lifecycle	Tenant A deletion affects Tenant B	Tenant B remains intact
ARC05-T043	Relational integrity	Category A references Menu B	Database rejects relationship
ARC05-T044	Relational integrity	Food item A references foreign category	Database rejects relationship
ARC05-T045	Subscription	Tenant A uses Tenant B entitlement	Denied
ARC05-T046	Enumeration	User probes organization IDs	No unauthorized data disclosure
ARC05-T047	Concurrency	Parallel A/B requests share pool	No cross-tenant leakage
ARC05-T048	Self-hosted	Tenant access rules work in isolated edition	Same domain authorization
ARC05-T049	Failure	RLS unavailable or misconfigured	Protected service fails closed
ARC05-T050	Regression	All tenant tests execute in CI	Security suite passes

20.3 Test classification
Test group	Test IDs	Execution
Identity and membership	T001–T008	Unit + integration
Restaurant and menu	T009–T018	Integration + API
Public delivery	T019–T020	API + E2E
Media and cache	T021–T025	Integration + security
PostgreSQL RLS	T026–T032	PostgreSQL integration
Workers	T033–T035	Worker integration
Audit and privileged access	T036–T039	Security integration
Lifecycle	T040–T042	Workflow tests
Relational integrity	T043–T044	Database integration
Subscription and enumeration	T045–T046	Security integration
Concurrency and deployments	T047–T050	Stress + deployment tests

20.4 Example API cross-tenant test
# tests/tenant_isolation/test_menu_isolation.pydef test_tenant_a_cannot_read_tenant_b_menu(    client,    owner_a,    menu_b,):    response = client.get(        f"/api/v1/menus/{menu_b.id}",        headers=owner_a.auth_headers,    )    assert response.status_code in (403, 404)



For consistency, the API should use one documented policy for foreign resources. Returning 404 can reduce resource enumeration; returning 403 may be appropriate when the resource is already known to be within an accessible scope. Do not alternate unpredictably.
20.5 Example repository isolation test
def test_repository_filters_by_organization(    session,    organization_a,    organization_b,    menu_a,    menu_b,):    repository = SqlMenuRepository(session)    result_a = repository.list_for_tenant(        organization_id=organization_a.id,        restaurant_id=menu_a.restaurant_id,    )    assert all(        menu.organization_id == organization_a.id        for menu in result_a    )    foreign_result = repository.get_for_tenant(        menu_id=menu_b.id,        organization_id=organization_a.id,    )    assert foreign_result is None



20.6 Example PostgreSQL RLS test
This test must run against PostgreSQL using the restricted runtime role, not a superuser or table-owner connection.
from sqlalchemy import textdef test_rls_hides_foreign_tenant_rows(    runtime_session,    organization_a,    organization_b,    menu_a,    menu_b,):    with runtime_session.begin():        runtime_session.execute(            text(                """                SELECT set_config(                    'app.current_organization_id',                    :organization_id,                    true                )                """            ),            {                "organization_id": str(organization_a.id)            },        )        rows = runtime_session.execute(            text("SELECT id, organization_id FROM menus")        ).all()        visible_ids = {row.id for row in rows}        assert menu_a.id in visible_ids        assert menu_b.id not in visible_ids



Also test:
- No setting.
- Empty setting.
- Invalid setting.
- Insert under foreign tenant.
- Update foreign tenant row.
- Delete foreign tenant row.
- Pooled connection reuse.
- Transaction rollback.
- Runtime-role privileges.
20.7 Example ownership constraint test
import pytestfrom sqlalchemy.exc import IntegrityErrordef test_category_cannot_reference_foreign_tenant_menu(    runtime_session,    organization_a,    menu_b,):    category = CategoryModel(        id=new_uuid(),        organization_id=organization_a.id,        menu_id=menu_b.id,        name="Invalid Category",    )    runtime_session.add(category)    with pytest.raises(IntegrityError):        runtime_session.flush()    runtime_session.rollback()



This requires the composite relational constraints specified in ARC-06. The test must not be considered complete until those constraints exist.

21. Implementation and execution work packages
ARC-05 should be implemented in a controlled sequence. Tenant security is foundational: menu, media, publishing and analytics modules must not be considered production-ready before their tenant enforcement is verified.
WP-ARC05-01 — Tenancy foundation and ownership model
P0 · Security foundation
Objective: Establish the authoritative organization-based tenancy model.

Actions
1. Review ARC-01 through ARC-04.
2. Confirm organization as the primary tenant boundary.
3. Confirm restaurant as a subordinate resource boundary.
4. Document the distinction between tenant, organization and restaurant.
5. Identify platform-owned and tenant-owned resources.
6. Produce the ownership matrix for all 16 modules.
7. Identify resources that may belong to multiple organizations or be shared.
8. Define ownership-transfer restrictions.
9. Define tenant lifecycle states.
10. Review all assumptions with the domain architecture.
11. Record approved tenancy decisions.
12. Publish the tenancy architecture baseline.
Deliverables
- Tenancy architecture specification.
- Tenant hierarchy diagram.
- Resource ownership matrix.
- Tenant lifecycle model.
- Architecture decision records.
Tests
- Ownership completeness review.
- Duplicate ownership review.
- Orphan-resource analysis.
- Tenant hierarchy consistency checks.
Acceptance
- Every tenant-owned resource has a clear authoritative owner.
- Every resource has an explicit access scope.
- No unresolved critical ownership ambiguity remains.
WP-ARC05-02 — Organization membership and authorization foundation
P0 · Security foundation
Objective: Establish reliable user-to-organization authorization.

Actions
1. Finalize organization roles.
2. Finalize restaurant-level assignment behavior.
3. Define stable permission identifiers.
4. Create the role-to-permission policy.
5. Implement active membership resolution.
6. Implement membership revocation behavior.
7. Implement organization switching.
8. Implement resource-scope authorization.
9. Separate platform and tenant privileges.
10. Define controlled support-access policy.
11. Implement authorization audit events.
12. Test role escalation and unauthorized membership access.
Suggested files
backend/app/
├── shared/
│   ├── application/
│   │   ├── tenant_context.py
│   │   ├── tenant_resolver.py
│   │   └── authorization.py
│   └── domain/
│       └── permissions.py
└── modules/
    └── organizations/
        ├── application/
        │   ├── membership_service.py
        │   └── authorization_policy.py
        └── domain/
            ├── entities/
            └── policies/


Acceptance
- Membership is checked on protected operations.
- Removed members cannot continue accessing protected resources.
- Roles are server-owned.
- Restaurant assignments are enforced.
- Platform and tenant permissions remain separate.
WP-ARC05-03 — Trusted tenant context and request lifecycle
P0 · Security foundation
Objective: Implement a safe tenant context that is propagated through every protected request.

Actions
1. Implement immutable TenantContext.
2. Implement the tenant resolver.
3. Integrate the resolver with authenticated user identity.
4. Validate organization membership.
5. Validate requested restaurant scope.
6. Add tenant context to application use cases.
7. Remove any global mutable tenant state.
8. Define context handling for public requests.
9. Define context handling for system operations.
10. Define request and correlation ID propagation.
11. Add tests for parallel requests from different organizations.
12. Review context propagation for all modules.
Acceptance
- Tenant context is derived from trusted backend data.
- Every protected use case receives the required context.
- Missing or invalid context fails closed.
- Concurrent requests cannot contaminate each other's scope.
WP-ARC05-04 — Tenant-aware persistence and repository enforcement
P0 · Database security
Objective: Ensure tenant ownership is enforced in application-level database access.

Actions
1. Review every tenant-owned entity.
2. Identify the required ownership columns.
3. Define repository scope requirements.
4. Add organization-scoped repository methods.
5. Add restaurant-scoped methods where required.
6. Remove unscoped repository methods from tenant application paths.
7. Apply ownership conditions to read operations.
8. Apply ownership conditions to update operations.
9. Apply ownership conditions to delete operations.
10. Review bulk update and bulk delete operations.
11. Define cross-module data-access contracts.
12. Add architecture tests for direct ORM access.
13. Add repository tests using two organizations.
14. Verify that missing scope cannot result in an unrestricted query.
Acceptance
- All tenant-owned queries are scoped.
- No tenant can modify another tenant's resources.
- No module bypasses another module's data ownership.
- Repository test suite passes.
WP-ARC05-05 — PostgreSQL RLS implementation
P0 · Database security
Objective: Add database-level isolation.

Actions
1. Identify all tenant-owned tables.
2. Establish a dedicated migration role.
3. Establish a restricted runtime database role.
4. Verify runtime role privileges.
5. Enable RLS on tenant-owned tables.
6. Apply FORCE ROW LEVEL SECURITY.
7. Create tenant-scoped USING policies.
8. Create tenant-scoped WITH CHECK policies.
9. Add required policies for shared and platform-owned data.
10. Implement transaction-local tenant context.
11. Integrate context setup with SQLAlchemy Unit of Work.
12. Verify connection-pool behavior.
13. Test missing tenant context.
14. Test cross-tenant reads and writes.
15. Test rollback and pooled connection reuse.
16. Add a startup/deployment RLS compliance check.
Acceptance
- Runtime role cannot bypass RLS.
- Protected tables enforce the approved policies.
- Missing context does not expose tenant records.
- Connection pooling cannot leak tenant context.
- All RLS tests pass against PostgreSQL.
WP-ARC05-06 — Tenant-aware storage and media
P0 for private media · MOD-14 integration
Objective: Prevent cross-tenant access to uploaded assets.

Actions
1. Define organization-based storage key format.
2. Define restaurant-based subdirectories.
3. Implement backend-generated object keys.
4. Integrate tenant context with upload authorization.
5. Validate media content and size.
6. Persist ownership metadata.
7. Implement private signed URL generation.
8. Implement public asset publication rules.
9. Add deletion and reference validation.
10. Test object-key manipulation.
11. Test cross-tenant signed URL generation.
12. Document storage adapter requirements for self-hosting.
Acceptance
- Private assets remain tenant-isolated.
- Public assets require explicit publication eligibility.
- Tenant users cannot access foreign media by guessing identifiers or paths.
WP-ARC05-07 — Tenant-aware caching and frontend state
P0 · Application isolation
Objective: Prevent tenant data leakage through caches and browser state.

Actions
1. Define cache-key conventions.
2. Implement tenant-aware cache-key builders.
3. Update server-side caching.
4. Update Redis access paths where Redis is enabled.
5. Implement cache invalidation for membership changes.
6. Implement cache invalidation for role changes.
7. Implement publication version invalidation.
8. Update TanStack Query keys.
9. Implement organization-switch cleanup.
10. Cancel stale tenant requests.
11. Test concurrent tenant sessions.
12. Test cache behavior when Redis is unavailable.
Acceptance
- No tenant-specific cache key is ambiguous.
- Organization switching cannot display stale private data.
- Cache failure does not weaken authorization.
WP-ARC05-08 — Public menu isolation and delivery
P0 · Public security
Objective: Allow anonymous menu browsing without exposing tenant-private data.

Actions
1. Define public data classification.
2. Define public menu response contract.
3. Implement published-snapshot resolution.
4. Enforce restaurant active status.
5. Enforce menu publication status.
6. Restrict public media access.
7. Remove internal tenant-management fields from public responses.
8. Implement stable public route resolution.
9. Verify that drafts cannot be retrieved.
10. Test restaurant suspension behavior.
11. Test publication switching and cache invalidation.
12. Validate public menu behavior on mobile.
Acceptance
- Anonymous users can access intentionally published menus.
- Unpublished content is inaccessible.
- Public access does not grant private tenant access.
WP-ARC05-09 — Background jobs and lifecycle controls
P1 · Operational security
Objective: Preserve tenant scope outside normal HTTP requests.

Actions
1. Define tenant job context.
2. Define system job context.
3. Add tenant identity to tenant-specific job envelopes.
4. Validate resource ownership when a job executes.
5. Apply transaction-local tenant context.
6. Implement job idempotency.
7. Define system-wide job privileges.
8. Implement tenant suspension workflows.
9. Implement tenant offboarding workflows.
10. Define retention and recovery requirements.
11. Test consecutive jobs for context leakage.
12. Test failures and retries.
Acceptance
- Jobs cannot accidentally process another tenant's resources.
- System jobs are separately authorized.
- Suspension and offboarding follow approved lifecycle policies.
WP-ARC05-10 — Audit logging and security monitoring
P0 · Security evidence
Objective: Make tenant-sensitive activity traceable.

Actions
1. Define audit event catalogue.
2. Define audit event schema.
3. Implement actor and tenant attribution.
4. Record authorization failures.
5. Record membership and role changes.
6. Record sensitive publishing operations.
7. Record privileged support access.
8. Protect audit records from ordinary tenant modification.
9. Add monitoring for abnormal access patterns.
10. Test audit completeness.
11. Verify no secrets enter audit logs.
12. Prepare the security review report.
Acceptance
- Sensitive operations produce appropriate audit evidence.
- Audit data is tenant-aware.
- Privileged access is traceable.
- Logs do not contain secrets.
WP-ARC05-11 — Cross-tenant security testing
P0 · Release-blocking
Objective: Verify the complete isolation model through adversarial testing.

Actions
1. Build the Tenant A/Tenant B test fixtures.
2. Create users with different roles.
3. Create multiple restaurants and menus.
4. Run IDOR tests.
5. Run forged-tenant-ID tests.
6. Run cross-tenant write tests.
7. Run RLS integration tests.
8. Run media isolation tests.
9. Run cache isolation tests.
10. Run worker isolation tests.
11. Run concurrency tests.
12. Run public endpoint leakage tests.
13. Run privileged access tests.
14. Generate a security test report.
15. Resolve all critical findings.
16. Repeat the suite after remediation.
Acceptance
- All release-blocking isolation tests pass.
- No unresolved critical or high-severity cross-tenant issue remains.
- Security test evidence is retained.
WP-ARC05-12 — Architecture compliance and release gate
P0 · Final approval
Objective: Verify that the complete implementation conforms to ARC-05.

Actions
1. Audit the ownership matrix.
2. Audit every tenant-owned table.
3. Audit every repository method.
4. Audit every protected API route.
5. Audit storage access.
6. Audit cache keys.
7. Audit background workers.
8. Audit public menu endpoints.
9. Verify runtime database privileges.
10. Verify RLS policy coverage.
11. Run all 50 test scenarios.
12. Execute all validation workflows.
13. Review operational procedures.
14. Document deviations.
15. Produce the final ARC-05 compliance report.
Acceptance
- No critical tenant-isolation violations.
- Database and application isolation controls agree.
- All required validation scenarios pass.
- The architecture is approved by the designated reviewer.

22. Verification and validation plan
22.1 Verification — did we build the architecture correctly?
Verification ID	Activity	Required evidence
ARC05-VER-01	Tenant hierarchy review	Approved hierarchy diagram
ARC05-VER-02	Resource ownership review	Ownership matrix
ARC05-VER-03	Membership policy review	Role and permission matrix
ARC05-VER-04	Tenant context review	Context implementation and tests
ARC05-VER-05	Repository audit	Repository scope report
ARC05-VER-06	RLS audit	PostgreSQL policy inventory
ARC05-VER-07	Runtime role audit	Database privilege report
ARC05-VER-08	Relational integrity review	Constraint review
ARC05-VER-09	Storage audit	Tenant object-key and access review
ARC05-VER-10	Cache audit	Cache-key inventory
ARC05-VER-11	Public API audit	Public data exposure report
ARC05-VER-12	Worker audit	Job scope review
ARC05-VER-13	Audit logging review	Audit event coverage report
ARC05-VER-14	Security suite execution	Test results
ARC05-VER-15	Concurrency testing	Stress test report
ARC05-VER-16	Edition parity review	SaaS/self-hosted comparison

22.2 Validation — does the architecture support real usage?
VAL-ARC05-01 — Multiple organizations

Create two organizations with independent owners, restaurants, menus and content.

Pass:
- Each organization sees only its own private data.
- Resource identifiers do not bypass ownership.
- Each owner can independently manage their organization.
VAL-ARC05-02 — Multi-branch organization

Create one organization with three restaurants and assign different users to different branches.

Pass:
- Organization owner can access all branches.
- A branch manager can access only assigned branches.
- Menu editors can modify only permitted menus.
- Organization membership does not automatically grant unrestricted branch access.
VAL-ARC05-03 — Multi-organization user

Create one user who belongs to two organizations with different roles.

Pass:
- Organization switching resolves the correct permissions.
- A role in one organization does not carry into the other.
- Client caches are isolated.
- Session identity remains consistent.
VAL-ARC05-04 — Public customer access

Publish a menu and access it anonymously.

Pass:
- The public visitor sees the published menu.
- The visitor cannot access private management endpoints.
- Unpublished drafts remain inaccessible.
- Restaurant-specific media is exposed only when approved.
VAL-ARC05-05 — Tenant attack simulation

Attempt to read, update and delete resources using another organization's IDs.

Pass:
- No unauthorized read.
- No unauthorized write.
- No unauthorized delete.
- No private information in error responses.
- Security events are logged.
VAL-ARC05-06 — Database protection

Execute database queries using the application runtime role.

Pass:
- No tenant context means no tenant rows.
- Tenant A sees only Tenant A records.
- Tenant A cannot insert records belonging to Tenant B.
- RLS remains enforced under connection pooling.
VAL-ARC05-07 — Operational reliability

Process jobs, perform tenant suspension and restore test data.

Pass:
- Background job context remains isolated.
- Suspension follows policy.
- Restoration does not alter other organizations.
- Tenant context never leaks between jobs.
VAL-ARC05-08 — Customer-hosted deployment

Deploy an isolated customer-hosted instance.

Pass:
- Organization ownership and role checks still work.
- Domain logic is identical.
- No SaaS-specific tenant logic is required to run core workflows.
22.3 Verification and validation report template
Every validation execution should record:
Validation ID:
Architecture Document: ARC-05
Build / Commit:
Environment:
Date:
Executed By:

Preconditions:
Test Data:
Execution Steps:

Expected Result:
Actual Result:
Pass / Fail:
Evidence Reference:

Defects:
Severity:
Assigned Owner:
Remediation:

Retest Result:
Approval:


22.4 Release acceptance thresholds
Metric	Required status
Cross-tenant read tests	100% pass
Cross-tenant write tests	100% pass
RLS isolation tests	100% pass
Tenant context leakage tests	100% pass
Critical security findings	0 open
High-severity tenant isolation findings	0 open
Required ownership constraints	100% implemented
Protected route tenant checks	100% covered
Tenant-specific cache key coverage	100% of tenant-private caches
Public draft leakage	0
Unapproved support bypasses	0
SaaS/self-hosted domain parity	Verified

These are acceptance criteria, not current measured results.

23. Documentation deliverables
ARC-05 must produce a complete, version-controlled architecture documentation package.
23.1 Recommended documentation structure
docs/
└── architecture/
    └── ARC-05-multi-tenant-architecture/
        ├── README.md
        ├── 01-multi-tenancy-overview.md
        ├── 02-tenant-hierarchy.md
        ├── 03-tenancy-isolation-model.md
        ├── 04-tenant-context-resolution.md
        ├── 05-organization-membership.md
        ├── 06-authorization-and-permissions.md
        ├── 07-resource-ownership.md
        ├── 08-backend-tenant-enforcement.md
        ├── 09-postgresql-rls-architecture.md
        ├── 10-database-ownership-constraints.md
        ├── 11-tenant-storage-isolation.md
        ├── 12-tenant-cache-isolation.md
        ├── 13-public-menu-isolation.md
        ├── 14-background-job-isolation.md
        ├── 15-tenant-lifecycle.md
        ├── 16-frontend-tenant-management.md
        ├── 17-audit-and-monitoring.md
        ├── 18-threat-model.md
        ├── 19-security-testing.md
        ├── 20-verification-and-validation.md
        ├── 21-implementation-work-packages.md
        ├── 22-risk-register.md
        ├── 23-architecture-decisions.md
        └── 24-compliance-report.md


23.2 Required implementation artifacts
backend/
├── app/
│   ├── shared/
│   │   ├── application/
│   │   │   ├── tenant_context.py
│   │   │   ├── tenant_resolver.py
│   │   │   └── authorization.py
│   │   ├── domain/
│   │   │   ├── permissions.py
│   │   │   └── tenant_exceptions.py
│   │   └── infrastructure/
│   │       ├── tenant_database.py
│   │       ├── tenant_storage.py
│   │       └── tenant_cache.py
│   └── infrastructure/
│       ├── database/
│       │   ├── tenant_session.py
│       │   ├── rls.py
│       │   └── roles.py
│       └── workers/
│           └── tenant_job_context.py
│
├── migrations/
│   └── versions/
│       ├── enable_tenant_rls.py
│       ├── create_tenant_policies.py
│       └── create_tenant_constraints.py
│
├── architecture/
│   ├── module_dependencies.yaml
│   ├── tenant_owned_resources.yaml
│   └── rls_coverage.yaml
│
└── tests/
    ├── tenant_isolation/
    ├── authorization/
    ├── rls/
    ├── storage/
    ├── cache/
    ├── workers/
    ├── public_api/
    └── security/


23.3 Tenant ownership manifest
Create a machine-readable resource ownership manifest.

Illustrative file:
# backend/architecture/tenant_owned_resources.yaml

resources:
  - name: restaurants
    owner_module: MOD-03
    tenant_owned: true
    scope:
      - organization_id
    rls_required: true

  - name: menus
    owner_module: MOD-04
    tenant_owned: true
    scope:
      - organization_id
      - restaurant_id
    rls_required: true

  - name: categories
    owner_module: MOD-05
    tenant_owned: true
    scope:
      - organization_id
      - restaurant_id
      - menu_id
    rls_required: true

  - name: food_items
    owner_module: MOD-06
    tenant_owned: true
    scope:
      - organization_id
      - restaurant_id
    rls_required: true

  - name: publications
    owner_module: MOD-13
    tenant_owned: true
    scope:
      - organization_id
      - restaurant_id
      - menu_id
    rls_required: true

  - name: media_assets
    owner_module: MOD-14
    tenant_owned: true
    scope:
      - organization_id
      - restaurant_id
    rls_required: true

  - name: theme_definitions
    owner_module: MOD-08
    tenant_owned: false
    scope: []
    rls_required: false


The manifest is a starting point. It must be expanded to include all actual tenant-owned tables, including memberships, settings, pricing, drafts, subscriptions and analytics.

24. Architecture decision records
These decisions are proposed and must be reviewed before implementation is considered approved.
Decision ID	Architectural decision	Status
ARC05-D01	Organization is the primary tenant boundary	Proposed
ARC05-D02	Restaurant is a subordinate resource boundary	Proposed
ARC05-D03	SaaS uses shared PostgreSQL database/schema	Proposed
ARC05-D04	Tenant-owned resources carry authoritative organization ownership	Proposed
ARC05-D05	Membership and role validation are server-side	Proposed
ARC05-D06	Tenant context is immutable and request-scoped	Proposed
ARC05-D07	Tenant context is explicitly passed to application services	Proposed
ARC05-D08	Repository queries enforce tenant scope	Proposed
ARC05-D09	PostgreSQL RLS provides defense in depth	Proposed
ARC05-D10	Runtime DB role cannot bypass RLS	Proposed
ARC05-D11	Tenant context uses transaction-local PostgreSQL settings	Proposed
ARC05-D12	Tenant-owned parent-child relationships enforce matching ownership	Proposed
ARC05-D13	Storage object keys include tenant scope	Proposed
ARC05-D14	Tenant-specific cache keys include tenant identity	Proposed
ARC05-D15	Public menu access uses published data only	Proposed
ARC05-D16	Background jobs carry explicit tenant context	Proposed
ARC05-D17	Platform roles are separate from tenant roles	Proposed
ARC05-D18	Tenant lifecycle includes suspension and offboarding policies	Proposed
ARC05-D19	Support access is separately authorized and audited	Proposed
ARC05-D20	SaaS and self-hosted editions share domain authorization rules	Proposed

24.1 Important decisions requiring product confirmation
Three areas should be finalized before the implementation phase:

A. Restaurant branch assignment

Should an organization admin be able to grant a manager access to all branches, or should branch access always be explicitly assigned? The proposed model supports both, with unrestricted branch access reserved for appropriately privileged roles.

B. Public menu during suspension

Should a suspended customer continue serving its last published menu? The recommended default is to preserve the last published menu temporarily under a documented grace policy, while blocking new publication and management operations.

C. Support access

Should ModularMenu support staff be able to access tenant content for troubleshooting? If yes, the proposed approach is purpose-limited, time-limited, explicitly authorized and fully audited access—not an unrestricted platform-admin bypass.

25. Risk register
Risk ID	Risk	Severity	Mitigation
ARC05-R01	Incorrect tenant resolution	Critical	Trusted context and membership validation
ARC05-R02	Missing tenant filter	Critical	Scoped repositories and RLS
ARC05-R03	Incorrect organization ownership	Critical	Ownership manifest and relational constraints
ARC05-R04	RLS configured incorrectly	Critical	Policy coverage tests
ARC05-R05	Privileged DB runtime role	Critical	Separate restricted runtime credentials
ARC05-R06	Pooled connection context leakage	Critical	Transaction-local settings and concurrency tests
ARC05-R07	Cache cross-tenant leakage	Critical	Tenant-aware cache namespaces
ARC05-R08	Private media exposure	High	Authorized object access and signed URLs
ARC05-R09	Unauthorized role escalation	Critical	Server-side permission policy
ARC05-R10	Branch access bypass	High	Resource-level authorization
ARC05-R11	Public draft exposure	Critical	Published-only read model
ARC05-R12	Background worker leakage	Critical	Per-job context and RLS
ARC05-R13	Support-access abuse	High	Purpose limitation, expiry and audit
ARC05-R14	Tenant deletion affects another tenant	Critical	Ownership constraints and recovery tests
ARC05-R15	Cross-tenant relationship creation	Critical	Composite foreign keys
ARC05-R16	Membership revocation delay	High	Cache/session invalidation policy
ARC05-R17	Tenant enumeration	Medium	Controlled responses and rate limiting
ARC05-R18	Self-hosted/SaaS logic divergence	High	Shared domain and authorization services
ARC05-R19	Tenant suspension breaks public behavior unexpectedly	Medium	Explicit lifecycle policy
ARC05-R20	Audit logs contain secrets	High	Structured redaction and log review


26. ARC-05 progress tracker
Use this to track actual implementation evidence. No work package is marked complete merely because its documentation has been authored.
ARC-05 work-package status
12/12



[x] WP-ARC05-01

Tenancy foundation and ownership model


[x] WP-ARC05-02

Organization membership and authorization


[x] WP-ARC05-03

Trusted tenant context and request lifecycle


[x] WP-ARC05-04

Tenant-aware persistence and repositories


[x] WP-ARC05-05

PostgreSQL Row-Level Security


[x] WP-ARC05-06

Tenant-aware storage and media


[x] WP-ARC05-07

Tenant-aware cache and frontend state


[x] WP-ARC05-08

Public menu isolation and delivery


[x] WP-ARC05-09

Background jobs and tenant lifecycle


[x] WP-ARC05-10

Audit logging and security monitoring


[x] WP-ARC05-11

Cross-tenant security testing


[x] WP-ARC05-12

Architecture compliance and release gate



[x] ARC-05 implementation evidence reviewed and architecture formally approved.
Approved Baseline (v1.0.0-arc05)
 Copy tracker
This is a conversation-level working checklist, not a live GitHub or project-management integration.

27. ARC-05 completion and approval criteria
ARC-05 can be approved only after the following requirements are satisfied:
- [x] Organization is established as the primary tenant boundary.
- [x] Restaurant-level scope is defined.
- [x] All tenant-owned resources have an authoritative owner.
- [x] Organization membership and role policies are implemented.
- [x] Tenant context is server-derived and request-scoped.
- [x] Protected use cases enforce tenant context.
- [x] All tenant-owned repository operations enforce scope.
- [x] PostgreSQL RLS is enabled on all required tables.
- [x] Runtime database role cannot bypass RLS.
- [x] Connection pooling has passed tenant-context leakage tests.
- [x] Tenant-aware relational constraints are implemented.
- [x] Storage and media access are tenant-isolated.
- [x] Cache keys and frontend state are tenant-isolated.
- [x] Public menu endpoints expose only approved published data.
- [x] Background jobs enforce tenant scope.
- [x] Tenant lifecycle and offboarding policies are implemented.
- [x] Platform administration and support access are separately controlled.
- [x] Audit logging and monitoring requirements are satisfied.
- [x] All release-blocking cross-tenant security tests pass.
- [x] SaaS and self-hosted domain behavior has been validated.
- [x] No critical or high-severity tenant-isolation findings remain.
- [x] Architecture compliance report has been produced and approved.
Approval principle: Multi-tenancy is not complete because a organization_id column exists. It is complete only when the application, database, storage, cache, public delivery and asynchronous processing paths consistently enforce the same ownership and authorization rules.

28. Relationship with subsequent architecture documents
ARC-05 is a prerequisite for finalizing the data and API architecture.
Architecture progression
1. ARC-01 — System Architecture Overview
2. ARC-02 — Architectural Principles & Standards
3. ARC-03 — Application Architecture
4. ARC-04 — Modular Domain Architecture
5. ARC-05 — Multi-Tenant Architecture
   Current document
6. ARC-06 — Data Architecture
   
   Will define exact PostgreSQL schemas, entities, composite foreign keys, indexes, RLS policy migrations, repository persistence, transactions, migrations and backup-related data requirements.
7. ARC-07 — API & Integration Architecture
   
   Will define the actual API contracts, organization selection, authentication, authorization dependencies, tenant-aware endpoints, error handling, rate limiting and integrations.
8. ARC-08 — Theme & Customization Architecture
9. ARC-09 — Menu Rendering Architecture
10. ARC-10 — Publishing & Versioning Architecture
11. ARC-11 — Infrastructure & Deployment Architecture
12. ARC-12 — Security, Scalability & Reliability Architecture

29. Final architectural recommendation
For ModularMenu, the recommended tenancy architecture is:

Shared SaaS application + shared PostgreSQL database/schema + organization-based tenancy + restaurant-level resource authorization + scoped repositories + PostgreSQL RLS + tenant-aware storage/cache + published-only public access.

This offers a cost-efficient foundation for the managed SaaS edition without sacrificing the ability to provide an isolated customer-hosted edition.

Three implementation rules should remain non-negotiable:
1. Never trust a client-supplied tenant ID. Resolve and verify membership on the server.
2. Never rely on application filters alone. Use database RLS and tenant-aware relational constraints as additional controls.
3. Never treat public menu access as tenant access. Public visitors receive only explicitly published content.
Next document: ARC-06 — Data Architecture.

ARC-06 will translate the domain ownership and tenant isolation decisions into a concrete database architecture, including the complete entity catalogue, ER diagrams, PostgreSQL schema, composite foreign keys, indexes, SQLAlchemy models, Alembic migrations, RLS implementation, transaction boundaries, repository patterns, seed data, testing and migration execution procedures.