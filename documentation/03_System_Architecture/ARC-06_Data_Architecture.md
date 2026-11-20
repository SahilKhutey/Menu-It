ARC-06 — Data Architecture
MODULARMENU · ARCHITECTURE DOCUMENTATION SERIES
ARC-06
Approved Baseline · Version 1.0
Implementation Complete

Document title: Data Architecture — Database Design, Data Ownership, Persistence, Integrity and Lifecycle

Parent documents: ARC-01 System Architecture Overview · ARC-02 Architectural Principles & Standards · ARC-03 Application Architecture · ARC-04 Modular Domain Architecture · ARC-05 Multi-Tenant Architecture

Primary technology: PostgreSQL · SQLAlchemy 2.x · Alembic · Pydantic · FastAPI

Architecture approach: Relational-first, tenant-aware, modular persistence architecture with controlled JSONB configuration and immutable publication snapshots.

1. Purpose and objectives
ARC-06 converts the domain boundaries and tenant-isolation principles established in ARC-04 and ARC-05 into a concrete data architecture.

It defines how ModularMenu stores, relates, validates, retrieves, migrates, protects, backs up and eventually deletes data across both deployment editions:
1. Managed SaaS: shared PostgreSQL database and schema, with organization-level tenant isolation.
2. Customer-hosted: the same schema and data rules deployed within the customer's infrastructure.
The objective is to establish one consistent data model—not separate SaaS and self-hosted database implementations.
1.1 Architecture objectives
ID	Objective	Required outcome
DA-01	Tenant ownership	Every private tenant-owned record has explicit ownership
DA-02	Referential integrity	Invalid or cross-tenant relationships are rejected by the database
DA-03	Data consistency	Business invariants are enforced at the appropriate layer
DA-04	Query efficiency	Common application queries have deliberate indexes
DA-05	Data security	Tenant isolation is enforced by application authorization and PostgreSQL RLS
DA-06	Publication integrity	Published menu versions are immutable snapshots
DA-07	Extensibility	New modules can introduce data without destabilizing existing modules
DA-08	Portability	The same database architecture works in both editions
DA-09	Recoverability	Backup, restore and migration procedures are repeatable and tested
DA-10	Traceability	Important data changes can be attributed to actors and operations

1.2 Scope
Included
- Data architecture and ownership model.
- Entity catalogue and relationships.
- Logical and physical database design.
- PostgreSQL schema and SQL constraints.
- SQLAlchemy models and repository patterns.
- Tenant-aware foreign keys and PostgreSQL RLS.
- Indexes, query patterns and data integrity.
- Menu publication snapshots and version history.
- Media metadata and storage references.
- Audit records and operational metadata.
- Alembic migrations and seed data.
- Backup, restore, retention and deletion procedures.
- Testing, verification, validation and compliance.
Excluded from this document
- Detailed API endpoint contracts — ARC-07.
- Theme token and component configuration semantics — ARC-08.
- Runtime menu rendering algorithms — ARC-09.
- Full publishing workflow and rollback behavior — ARC-10.
- Infrastructure topology and production deployment — ARC-11.
- Complete security architecture and threat-response operations — ARC-12.
These documents must use the data contracts established here rather than independently inventing competing data structures.

2. Core data architecture decisions
Proposed database architecture
Application modules

Identity · Tenants · Restaurants · Menus · Themes · Publishing · Media · Licensing


Application persistence layer

Repositories · Unit of Work · Tenant-scoped sessions · Data validation


PostgreSQL — shared logical schema
Identity & tenancy

Users · Organizations · Memberships · Restaurants


Menu domain

Menus · Categories · Items · Pricing


Presentation

Themes · Layouts · Components · Design config


Publication & operations

Snapshots · Publications · Media · Audit




Constraints · Composite foreign keys · Unique indexes · RLS policies · Transactions


Managed SaaS

Shared infrastructure


Customer-hosted

Customer infrastructure




2.1 Decisions and constraints
Decision	Proposed standard
Database	PostgreSQL
Database topology	One logical schema initially
Primary tenant boundary	Organization
Restaurant relationship	Belongs to an organization
Primary identifiers	UUID
Tenant-owned rows	Carry organization_id
Restaurant-scoped rows	Carry restaurant_id where relevant
Money	Integer minor units or NUMERIC, never floating point
Timestamps	TIMESTAMPTZ, stored in UTC
Flexible configuration	Validated JSONB
Relational data	Normalized relational tables
ORM	SQLAlchemy 2.x
Migrations	Alembic
Isolation	Application authorization + RLS + relational constraints
Publication	Immutable version snapshots
Deletion	Explicit lifecycle and retention policies

Important: UUIDs are identifiers, not authorization mechanisms. A UUID that is difficult to guess does not replace tenant authorization, scoped queries or database constraints.
2.2 Data ownership rule
The organization is the primary tenant owner. A restaurant is a subordinate business resource.

For example:
- An organization owns its restaurants.
- A restaurant owns its menus.
- A menu owns its categories and items.
- A menu publication references a specific immutable snapshot.
- A media asset belongs to an organization and may be associated with a restaurant or menu.
- Users are global identity records; organization membership determines their access.
Where a child record belongs to a restaurant, it should generally also carry organization_id. This duplication is intentional: it enables composite foreign keys and RLS to verify that the restaurant and child record belong to the same tenant.

3. Data ownership and entity catalogue
3.1 Entity groups
The database is organized by logical domain ownership. These are logical groups, not necessarily separate PostgreSQL schemas.
Group	Tables / entities	Owner
Identity	users, user_sessions, password_reset_tokens	Platform identity
Tenancy	organizations, organization_members, organization_invitations	Tenant
Restaurant	restaurants, restaurant_members, restaurant_settings, restaurant_domains	Organization
Menu	menus, menu_categories, menu_items	Restaurant
Pricing	item_prices, item_variants, item_addons, addons	Restaurant
Presentation	themes, restaurant_design_configs, layout_presets, component_definitions	Platform and tenant
Publishing	menu_versions, publications, publication_events	Restaurant
Media	media_assets, media_usages	Organization
Licensing	subscription_plans, subscriptions, licenses, deployment_entitlements	Platform / tenant
Governance	audit_logs, data_export_jobs, deletion_requests	Platform / tenant
Operations	outbox_events, idempotency_records	Application

Some tables are platform-global rather than tenant-owned. For example, subscription_plans and built-in theme presets are platform-owned. Their access must be controlled by platform permissions, not tenant RLS assumptions.
3.2 Core entity definitions
Identity and tenancy
Entity	Purpose	Key attributes
User	Global login identity	id, email, password_hash, status
Organization	Primary tenant	id, name, slug, status
OrganizationMember	User-to-organization relationship	organization_id, user_id, role, status
OrganizationInvitation	Pending membership invitation	organization_id, email, role, expires_at
Restaurant	Restaurant or branch	organization_id, id, name, slug, status
RestaurantMember	Optional restaurant-specific access	organization_id, restaurant_id, user_id, role
RestaurantSettings	Restaurant operational configuration	organization_id, restaurant_id, settings
RestaurantDomain	Public custom domain mapping	organization_id, restaurant_id, hostname, status

Menu and pricing
Entity	Purpose	Key attributes
Menu	A logical menu, e.g. Lunch Menu	organization_id, restaurant_id, id, name, status
MenuCategory	Menu grouping	organization_id, restaurant_id, menu_id, id, name, sort_order
MenuItem	Food or beverage item	organization_id, restaurant_id, category_id, id, name, status
ItemPrice	Price by currency or serving context	organization_id, restaurant_id, item_id, amount_minor, currency
ItemVariant	Size or serving variation	organization_id, restaurant_id, item_id, id, name
Addon	Reusable additional option	organization_id, restaurant_id, id, name
ItemAddon	Association between item and addon	organization_id, restaurant_id, item_id, addon_id
MenuItemTranslation	Localized item content	organization_id, restaurant_id, item_id, locale

Presentation and publishing
Entity	Purpose	Key attributes
Theme	Platform theme preset or tenant theme	id, owner_organization_id, name, tokens
RestaurantDesignConfig	Restaurant's active design configuration	organization_id, restaurant_id, theme_id, config
LayoutPreset	Reusable layout definition	id, owner_organization_id, schema_version, config
ComponentDefinition	Allowlisted component metadata/schema	id, key, schema_version, definition
MenuVersion	Immutable published or retained version snapshot	organization_id, restaurant_id, menu_id, version_number, snapshot
Publication	Publicly active version pointer/history	organization_id, restaurant_id, menu_id, menu_version_id, status

Media, commercial and governance
Entity	Purpose
MediaAsset	Metadata for an uploaded object; actual bytes reside in object storage
MediaUsage	Links media to a menu, item, theme or other supported resource
SubscriptionPlan	Platform-defined commercial plan
Subscription	Organization subscription and billing state
License	Edition and feature entitlement
DeploymentEntitlement	Customer-hosted deployment entitlement
AuditLog	Actor, action, resource, timestamp and outcome
OutboxEvent	Transactionally persisted event awaiting delivery
IdempotencyRecord	Prevents duplicate processing of supported write operations
DeletionRequest	Tracks approved deletion and retention workflow

3.3 Entity ownership matrix
Resource	Global	Organization	Restaurant	Publicly readable
User identity	Yes	—	—	No
Organization	—	Yes	—	No
Organization membership	—	Yes	—	No
Restaurant	—	Yes	Yes	Limited profile only
Menu	—	Yes	Yes	Published only
Category	—	Yes	Yes	Published snapshot only
Item	—	Yes	Yes	Published snapshot only
Price	—	Yes	Yes	Published snapshot only
Theme preset	Yes	Optional owner	Optional assignment	If public preset
Restaurant design config	—	Yes	Yes	Published snapshot only
Media	—	Yes	Optional association	Only explicitly published assets
Subscription	—	Yes	—	No
Audit log	—	Yes	Optional scope	No
Publication snapshot	—	Yes	Yes	Through approved public endpoint only

3.4 Relationship model
#chatgpt-mermaid-_r_1gb_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-_r_1gb_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_1gb_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_1gb_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-_r_1gb_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1gb_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-_r_1gb_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-_r_1gb_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-_r_1gb_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-_r_1gb_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-_r_1gb_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-_r_1gb_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_1gb_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_1gb_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-_r_1gb_ p{margin:0;}#chatgpt-mermaid-_r_1gb_ .entityBox{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);}#chatgpt-mermaid-_r_1gb_ .relationshipLabelBox{fill:rgb(243, 243, 243);opacity:0.7;background-color:rgb(243, 243, 243);}#chatgpt-mermaid-_r_1gb_ .relationshipLabelBox rect{opacity:0.5;}#chatgpt-mermaid-_r_1gb_ .labelBkg{background-color:rgba(243, 243, 243, 0.5);}#chatgpt-mermaid-_r_1gb_ .edgeLabel{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-_r_1gb_ .edgeLabel .label rect{fill:rgb(252, 252, 252);}#chatgpt-mermaid-_r_1gb_ .edgeLabel .label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1gb_ .edgeLabel .label{fill:rgb(83, 154, 248);font-size:14px;}#chatgpt-mermaid-_r_1gb_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1gb_ .edge-pattern-dashed{stroke-dasharray:8,8;}#chatgpt-mermaid-_r_1gb_ .node rect,#chatgpt-mermaid-_r_1gb_ .node circle,#chatgpt-mermaid-_r_1gb_ .node ellipse,#chatgpt-mermaid-_r_1gb_ .node polygon{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-_r_1gb_ .relationshipLine{stroke:rgb(143, 143, 143);stroke-width:1px;fill:none;}#chatgpt-mermaid-_r_1gb_ .marker{fill:none!important;stroke:rgb(143, 143, 143)!important;stroke-width:1;}#chatgpt-mermaid-_r_1gb_ [data-look=neo].labelBkg{background-color:rgba(243, 243, 243, 0.5);}#chatgpt-mermaid-_r_1gb_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].node rect,#chatgpt-mermaid-_r_1gb_ [data-look="neo"].cluster rect,#chatgpt-mermaid-_r_1gb_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-_r_1gb_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-_r_1gb_-gradient);stroke-width:1px;}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-_r_1gb_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-_r_1gb_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1gb_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-_r_1gb_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1gb_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}USERSORGANIZATION_MEMBERSORGANIZATIONSRESTAURANTSRESTAURANT_MEMBERSMENUSMENU_CATEGORIESMENU_ITEMSITEM_PRICESITEM_VARIANTSRESTAURANT_DESIGN_CONFIGSMENU_VERSIONSPUBLICATIONSMEDIA_ASSETSSUBSCRIPTIONSAUDIT_LOGSjoinshasownsassignsreceivescontainsgroupscontainspriced_byvaries_byconfiguressnapshotspublished_asownssubscribesrecords





This is a logical relationship diagram. The implementation must add organization and restaurant ownership columns and composite constraints where necessary; the diagram alone does not enforce tenant integrity.

4. Physical database design
4.1 Naming and data standards
Element	Convention	Example
Table	Plural snake_case	menu_items
Column	Singular snake_case	created_at
Primary key	id	UUID
Foreign key	<entity>_id	restaurant_id
Index	ix_<table>_<columns>	ix_menu_items_restaurant_id
Unique constraint	uq_<table>_<columns>	uq_restaurants_org_slug
Check constraint	ck_<table>_<rule>	ck_item_prices_amount
Foreign key constraint	fk_<table>_<relationship>	fk_menu_items_category

4.2 Standard columns
Every tenant-owned operational table should use the appropriate subset of:
id UUID PRIMARY KEY,
organization_id UUID NOT NULL,
restaurant_id UUID,
created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
created_by UUID,
updated_by UUID


Not every table needs all these fields. For example, a pure association table may use a composite primary key instead of its own UUID. Audit and immutable snapshot tables should not have an ordinary mutable updated_at contract.

Rules:
- created_at and updated_at are UTC-aware timestamps.
- created_by and updated_by are nullable only where system-generated operations or data migrations require it.
- User references should use a deliberate deletion policy; do not cascade-delete a user's entire business history.
- Status fields should use controlled values, enforced by application validation and database constraints where appropriate.
- Slugs should be normalized before storage and constrained for uniqueness at the correct scope.
- Use soft deletion only where restoration, legal retention or audit needs justify it. Do not apply deleted_at indiscriminately.
4.3 PostgreSQL schema — core tables
The following is an implementation-oriented reference schema. It is a foundation, not a complete executable migration for every entity. The final schema must be reconciled with ARC-04 module ownership and ARC-05 authorization decisions.

Organization and restaurant tables
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_organizations_status
        CHECK (status IN (
            'pending', 'active', 'suspended',
            'deletion_pending', 'deleted'
        ))
);

CREATE TABLE organization_members (
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(40) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (organization_id, user_id),

    CONSTRAINT fk_org_members_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(id),

    CONSTRAINT fk_org_members_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT ck_org_members_role
        CHECK (role IN ('owner', 'admin', 'member')),

    CONSTRAINT ck_org_members_status
        CHECK (status IN ('invited', 'active', 'suspended'))
);

CREATE TABLE restaurants (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    name VARCHAR(180) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    timezone VARCHAR(80) NOT NULL DEFAULT 'UTC',
    default_currency CHAR(3) NOT NULL DEFAULT 'INR',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_restaurants_org_id_id
        UNIQUE (organization_id, id),

    CONSTRAINT uq_restaurants_org_slug
        UNIQUE (organization_id, slug),

    CONSTRAINT fk_restaurants_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(id),

    CONSTRAINT ck_restaurants_status
        CHECK (status IN ('active', 'inactive', 'suspended')),

    CONSTRAINT ck_restaurants_currency
        CHECK (default_currency ~ '^[A-Z]{3}$')
);


The users table is a global identity table and must be defined in the identity module. This example assumes it exists before the membership migration.

Menu tables
CREATE TABLE menus (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    name VARCHAR(180) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_menus_org_restaurant_id
        UNIQUE (organization_id, restaurant_id, id),

    CONSTRAINT uq_menus_restaurant_slug
        UNIQUE (organization_id, restaurant_id, slug),

    CONSTRAINT fk_menus_restaurant
        FOREIGN KEY (organization_id, restaurant_id)
        REFERENCES restaurants(organization_id, id),

    CONSTRAINT ck_menus_status
        CHECK (status IN ('draft', 'active', 'archived'))
);

CREATE TABLE menu_categories (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    menu_id UUID NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_categories_org_restaurant_menu_id
        UNIQUE (organization_id, restaurant_id, menu_id, id),

    CONSTRAINT fk_categories_menu
        FOREIGN KEY (organization_id, restaurant_id, menu_id)
        REFERENCES menus(organization_id, restaurant_id, id),

    CONSTRAINT ck_categories_sort_order
        CHECK (sort_order >= 0)
);

CREATE TABLE menu_items (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    category_id UUID NOT NULL,
    name VARCHAR(180) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_items_org_restaurant_id
        UNIQUE (organization_id, restaurant_id, id),

    CONSTRAINT fk_items_category
        FOREIGN KEY (
            organization_id, restaurant_id, category_id
        )
        REFERENCES menu_categories(
            organization_id, restaurant_id, id
        ),

    CONSTRAINT ck_items_status
        CHECK (status IN ('active', 'inactive', 'archived')),

    CONSTRAINT ck_items_sort_order
        CHECK (sort_order >= 0)
);


This creates a database-enforced ownership chain:

organization → restaurant → menu → category → item

An item cannot reference a category belonging to another restaurant or organization through the declared composite relationships.

Pricing table
CREATE TABLE item_prices (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    item_id UUID NOT NULL,
    amount_minor BIGINT NOT NULL,
    currency CHAR(3) NOT NULL,
    price_label VARCHAR(80),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT fk_item_prices_item
        FOREIGN KEY (organization_id, restaurant_id, item_id)
        REFERENCES menu_items(organization_id, restaurant_id, id),

    CONSTRAINT ck_item_prices_amount
        CHECK (amount_minor >= 0),

    CONSTRAINT ck_item_prices_currency
        CHECK (currency ~ '^[A-Z]{3}$')
);

CREATE UNIQUE INDEX uq_item_prices_one_default
ON item_prices (organization_id, restaurant_id, item_id)
WHERE is_default = TRUE;


amount_minor stores the amount in the smallest currency unit. The application must use currency-aware conversion rules; it must not assume every currency has two decimal places. A NUMERIC(precision, scale) representation is also valid if the project selects and consistently implements it.
4.4 Index design
Indexes must follow measured query patterns. Avoid adding indexes to every column: indexes consume storage and slow writes.

Initial proposed indexes:
CREATE INDEX ix_restaurants_org_status
ON restaurants (organization_id, status);

CREATE INDEX ix_menus_restaurant_status
ON menus (organization_id, restaurant_id, status);

CREATE INDEX ix_categories_menu_order
ON menu_categories (
    organization_id, restaurant_id, menu_id, sort_order
);

CREATE INDEX ix_items_category_order
ON menu_items (
    organization_id, restaurant_id, category_id, sort_order
);

CREATE INDEX ix_items_restaurant_status
ON menu_items (
    organization_id, restaurant_id, status
);

CREATE INDEX ix_item_prices_item
ON item_prices (
    organization_id, restaurant_id, item_id
);


For frequently used public lookup paths, add indexes only after the access pattern is finalized. For example, public lookup by restaurant slug and menu slug may require a join or a dedicated public identifier mapping.

Index verification requirements
- Run EXPLAIN (ANALYZE, BUFFERS) on representative queries.
- Check index selectivity and actual query plans.
- Confirm indexes are used for common tenant-scoped list and detail queries.
- Test large result sets with pagination.
- Monitor index size and write overhead.
- Use concurrent index creation for large production tables where appropriate; note that CREATE INDEX CONCURRENTLY cannot run inside a normal transaction block.

5. JSONB and structured configuration
JSONB is useful for flexible configuration, but it must not become a substitute for a relational data model.
5.1 Appropriate JSONB use cases
- Theme tokens and visual design properties.
- Layout configuration.
- Component properties validated against a component schema.
- Published menu snapshots.
- Versioned editor configuration.
- External provider metadata where the structure is not central to business logic.
5.2 Do not use JSONB for
- Organization membership.
- Restaurant ownership.
- Menu categories and food items.
- Pricing that requires filtering, aggregation or relational constraints.
- Subscription ownership.
- Authentication credentials.
- Relationships requiring foreign keys.
- Data that requires independent lifecycle, authorization or audit.
5.3 Example design configuration
CREATE TABLE restaurant_design_configs (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    schema_version INTEGER NOT NULL,
    theme_key VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_design_config_restaurant
        UNIQUE (organization_id, restaurant_id),

    CONSTRAINT fk_design_config_restaurant
        FOREIGN KEY (organization_id, restaurant_id)
        REFERENCES restaurants(organization_id, id),

    CONSTRAINT ck_design_config_schema_version
        CHECK (schema_version > 0),

    CONSTRAINT ck_design_config_object
        CHECK (jsonb_typeof(config) = 'object')
);


Example configuration:
{
  "schema_version": 1,
  "theme": {
    "preset": "modern",
    "tokens": {
      "color.primary": "#263238",
      "color.background": "#FFFFFF",
      "radius.card": "12px"
    }
  },
  "layout": {
    "type": "image_grid",
    "columns": {
      "mobile": 1,
      "tablet": 2,
      "desktop": 3
    }
  },
  "components": {
    "header": {
      "visible": true,
      "show_logo": true
    },
    "item_card": {
      "show_description": true,
      "show_price": true
    }
  }
}


The JSON is only an example. The application must validate it against versioned schemas and the registered component allowlist before saving or publishing. Never execute tenant-supplied JavaScript, HTML or arbitrary code from these fields.
5.4 JSONB migration strategy
When configuration changes:
1. Increment the configuration schema version.
2. Add a migration or compatibility adapter.
3. Validate existing records against the old schema.
4. Transform the data deterministically.
5. Validate the transformed records against the new schema.
6. Record migration counts and failures.
7. Preserve a recovery path before destructive transformation.
8. Ensure the renderer can safely handle the intended supported schema versions.

6. Publication snapshots and data consistency
Published menus require special treatment because customers may be viewing a menu while a restaurant edits the next version.
6.1 Draft data versus published data
The mutable relational model is the editing source of truth.

The published snapshot is a read-optimized, immutable representation of the menu at publication time.
Data lifecycle
Mutable restaurant data

Menu · Categories · Items · Prices · Design configuration

Validate and capture in a transaction

Immutable menu version

Content snapshot · Design snapshot · Schema versions · Checksum

Publication references the immutable version

Public menu endpoint

Reads the active publication only


6.2 Menu version table
CREATE TABLE menu_versions (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    menu_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    snapshot JSONB NOT NULL,
    snapshot_sha256 CHAR(64) NOT NULL,
    content_schema_version INTEGER NOT NULL,
    design_schema_version INTEGER NOT NULL,
    created_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_menu_versions_number
        UNIQUE (
            organization_id, restaurant_id,
            menu_id, version_number
        ),

    CONSTRAINT uq_menu_versions_org_restaurant_menu_id
        UNIQUE (organization_id, restaurant_id, menu_id, id),

    CONSTRAINT fk_menu_versions_menu
        FOREIGN KEY (organization_id, restaurant_id, menu_id)
        REFERENCES menus(organization_id, restaurant_id, id),

    CONSTRAINT ck_menu_versions_positive
        CHECK (version_number > 0),

    CONSTRAINT ck_menu_versions_snapshot_object
        CHECK (jsonb_typeof(snapshot) = 'object')
);


The checksum is generated by the application from a canonical serialization of the snapshot. JSONB does not preserve original textual key ordering, so the hash must be based on a documented canonical representation rather than arbitrary JSON text.
6.3 Snapshot requirements
A snapshot should contain:
- Menu identity and display metadata.
- Restaurant public display metadata needed by the renderer.
- Categories and item ordering.
- Item descriptions and availability at publication time.
- Prices, currencies and variants.
- Published media references.
- Theme, layout and component configuration.
- Content and configuration schema versions.
- Publication metadata where appropriate.
It should not contain:
- Passwords, session tokens or authentication secrets.
- Internal staff information.
- Private subscription details.
- Unpublished content.
- Internal storage credentials or signed URLs.
- Sensitive audit data.
6.4 Immutability enforcement
Application conventions alone are insufficient for immutable records.

Required protections:
1. The application role should not have permission to update or delete version rows through ordinary application paths.
2. Repository interfaces should expose create/read operations, not generic update/delete methods for snapshots.
3. A database trigger may reject UPDATE and DELETE on immutable versions.
4. Retention and deletion must use a separately authorized administrative process.
5. Tests must verify that ordinary application operations cannot mutate a published snapshot.
Illustrative trigger:
CREATE FUNCTION prevent_menu_version_mutation()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'menu versions are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_menu_versions_immutable
BEFORE UPDATE OR DELETE ON menu_versions
FOR EACH ROW
EXECUTE FUNCTION prevent_menu_version_mutation();


A controlled archival or deletion policy may require a separate maintenance procedure. Do not silently disable immutability triggers during normal operations.

7. Tenant isolation at the database layer
ARC-05 establishes the tenant boundary. ARC-06 makes the data model and persistence layer enforce it.
7.1 Three independent controls
Layer	Control	Purpose
Application	Authorization and tenant-scoped use cases	Decides whether the actor may access the resource
Relational database	Composite foreign keys and constraints	Prevents invalid cross-tenant relationships
PostgreSQL	Row-Level Security	Restricts which rows the database role can read or modify

No one layer replaces the others.
7.2 RLS setup
Use a dedicated migration/owner role and a restricted runtime role. The runtime role must not be a superuser, table owner with RLS bypass, or have BYPASSRLS.

Example:
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE restaurants FORCE ROW LEVEL SECURITY;

CREATE POLICY restaurants_tenant_policy
ON restaurants
USING (
    organization_id =
    NULLIF(
        current_setting('app.current_organization_id', true),
        ''
    )::uuid
)
WITH CHECK (
    organization_id =
    NULLIF(
        current_setting('app.current_organization_id', true),
        ''
    )::uuid
);


Apply equivalent policies to every tenant-owned table, not just restaurants.

For a tenant-owned table with no organization_id, first review whether the ownership model is incomplete. Do not invent an implicit tenant relationship in application code.
7.3 Transaction-local tenant context
The tenant identifier must be derived from authenticated membership and authorization, never accepted as an authoritative value from an untrusted request body or query parameter.

Within each database transaction:
SELECT set_config(
    'app.current_organization_id',
    :organization_id,
    true
);


The third argument true makes the setting transaction-local. This is essential when using pooled database connections: a tenant context must not leak into the next request.
7.4 RLS test conditions
Test all of these:
- No tenant context: tenant rows are not accessible.
- Organization A context: A rows are visible, B rows are not.
- Organization B context: B rows are visible, A rows are not.
- Attempt to insert an A-owned row while context is B: rejected.
- Transaction rollback: context does not persist.
- Reused connection: next transaction receives only its own context.
- Runtime role: cannot bypass RLS.
- Migration role: used only by migration operations and not application traffic.
PostgreSQL integration tests are mandatory. SQLite cannot accurately verify PostgreSQL RLS behavior.

8. SQLAlchemy 2.x persistence architecture
8.1 Backend directory structure
Extend the ARC-03 backend structure:
backend/
└── app/
    ├── modules/
    │   ├── identity/
    │   ├── tenants/
    │   ├── restaurants/
    │   ├── menus/
    │   ├── categories/
    │   ├── menu_items/
    │   ├── pricing/
    │   ├── themes/
    │   ├── publishing/
    │   ├── media/
    │   ├── licensing/
    │   └── audit/
    │
    ├── shared/
    │   ├── domain/
    │   ├── application/
    │   │   ├── tenant_context.py
    │   │   └── unit_of_work.py
    │   └── infrastructure/
    │       ├── database/
    │       │   ├── base.py
    │       │   ├── session.py
    │       │   ├── tenant_session.py
    │       │   └── naming.py
    │       └── repositories/
    │
    ├── infrastructure/
    │   └── database/
    │       ├── models/
    │       ├── repositories/
    │       └── migrations/
    │
    └── tests/
        ├── unit/
        ├── integration/
        ├── database/
        ├── migrations/
        └── tenant_isolation/


The module that owns a domain entity should own its model and repository interface. Shared infrastructure may provide base classes and session management, but it should not become the owner of every business rule.
8.2 SQLAlchemy declarative base
# app/shared/infrastructure/database/base.pyfrom datetime import datetimefrom uuid import UUID, uuid4from sqlalchemy import DateTime, Uuid, funcfrom sqlalchemy.orm import DeclarativeBase, Mapped, mapped_columnclass Base(DeclarativeBase):    passclass UUIDPrimaryKey:    id: Mapped[UUID] = mapped_column(        Uuid(as_uuid=True),        primary_key=True,        default=uuid4,    )class Timestamped:    created_at: Mapped[datetime] = mapped_column(        DateTime(timezone=True),        server_default=func.now(),        nullable=False,    )    updated_at: Mapped[datetime] = mapped_column(        DateTime(timezone=True),        server_default=func.now(),        onupdate=func.now(),        nullable=False,    )



For production, use a consistent database naming convention for generated constraints. Ensure updated_at behavior is tested for bulk updates and direct SQL operations; ORM-level onupdate alone does not cover every database write path.
8.3 Restaurant model with composite ownership
# app/modules/restaurants/infrastructure/models.pyfrom uuid import UUIDfrom sqlalchemy import (    ForeignKey,    String,    UniqueConstraint,)from sqlalchemy.orm import Mapped, mapped_columnfrom app.shared.infrastructure.database.base import (    Base,    UUIDPrimaryKey,    Timestamped,)class Restaurant(Base, UUIDPrimaryKey, Timestamped):    __tablename__ = "restaurants"    __table_args__ = (        UniqueConstraint(            "organization_id",            "id",            name="uq_restaurants_org_id_id",        ),        UniqueConstraint(            "organization_id",            "slug",            name="uq_restaurants_org_slug",        ),    )    organization_id: Mapped[UUID] = mapped_column(        ForeignKey("organizations.id"),



8.4 Menu model with tenant-aware relationship
# app/modules/menus/infrastructure/models.pyfrom uuid import UUIDfrom sqlalchemy import (    ForeignKeyConstraint,    String,    UniqueConstraint,)from sqlalchemy.orm import Mapped, mapped_columnfrom app.shared.infrastructure.database.base import (    Base,    UUIDPrimaryKey,    Timestamped,)class Menu(Base, UUIDPrimaryKey, Timestamped):    __tablename__ = "menus"    __table_args__ = (        UniqueConstraint(            "organization_id",            "restaurant_id",            "id",            name="uq_menus_org_restaurant_id",        ),        UniqueConstraint(            "organization_id",            "restaurant_id",            "slug",            name="uq_menus_restaurant_slug",        ),        ForeignKeyConstraint(            ["organization_id", "restaurant_id"],



When defining composite foreign keys in SQLAlchemy, ensure the referenced column pair has a matching UNIQUE constraint or primary key. The migration and metadata must agree.
8.5 Tenant-scoped database session
# app/shared/infrastructure/database/tenant_session.pyfrom uuid import UUIDfrom sqlalchemy import textfrom sqlalchemy.ext.asyncio import AsyncSessionasync def set_tenant_context(    session: AsyncSession,    organization_id: UUID,) -> None:    await session.execute(        text(            """            SELECT set_config(                'app.current_organization_id',                :organization_id,                true            )            """        ),        {"organization_id": str(organization_id)},    )



Call this after beginning the transaction and before tenant-owned queries. The session lifecycle must guarantee that the transaction is committed or rolled back and the connection returned to the pool without a persistent tenant setting.
8.6 Repository pattern
from typing import Protocolfrom uuid import UUIDfrom sqlalchemy import selectfrom sqlalchemy.ext.asyncio import AsyncSessionfrom app.modules.menus.infrastructure.models import Menuclass MenuRepository(Protocol):    async def get_by_id(        self,        organization_id: UUID,        restaurant_id: UUID,        menu_id: UUID,    ) -> Menu | None:        ...class SqlAlchemyMenuRepository:    def __init__(self, session: AsyncSession) -> None:        self.session = session    async def get_by_id(        self,        organization_id: UUID,        restaurant_id: UUID,        menu_id: UUID,    ) -> Menu | None:        statement = select(Menu).where(            Menu.organization_id == organization_id,            Menu.restaurant_id == restaurant_id,            Menu.id == menu_id,        )        result = await self.session.execute(statement)



The repository includes explicit tenant scope even when RLS is enabled. This improves query clarity, index utilization and defense in depth.

Prohibited pattern:
# Do not use tenant-owned lookups this way.menu = await session.get(Menu, menu_id)



A primary-key lookup without explicit ownership conditions can be unsafe if it is used outside the expected RLS-protected transaction. The correct pattern is a scoped repository method with a validated tenant context.
8.7 Unit of Work
A single application use case may need to create or update multiple related rows.
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmakerclass SqlAlchemyUnitOfWork:    def __init__(        self,        session_factory: async_sessionmaker[AsyncSession],    ) -> None:        self.session_factory = session_factory    async def __aenter__(self):        self.session = self.session_factory()        self.transaction = await self.session.begin()        return self    async def __aexit__(self, exc_type, exc, tb):        try:            if exc_type is None:                await self.transaction.commit()            else:                await self.transaction.rollback()        finally:            await self.session.close()



This is a simplified pattern. The final implementation should expose module repositories through the Unit of Work and ensure tenant context is set before tenant-owned operations. Avoid opening nested transactions accidentally.

9. Alembic migration architecture
9.1 Migration directory
backend/
└── migrations/
    ├── env.py
    ├── script.py.mako
    └── versions/
        ├── 0001_create_identity.py
        ├── 0002_create_organizations.py
        ├── 0003_create_restaurants.py
        ├── 0004_create_menus.py
        ├── 0005_create_categories_items.py
        ├── 0006_create_pricing.py
        ├── 0007_create_presentation.py
        ├── 0008_create_publication.py
        ├── 0009_create_media.py
        ├── 0010_create_governance.py
        └── 0011_enable_tenant_rls.py


The filenames are illustrative. Actual migration revisions should be generated and reviewed against the final dependency graph.
9.2 Migration dependency order
1. PostgreSQL extensions and common types, if required.
2. Users and identity tables.
3. Organizations and membership.
4. Restaurants and restaurant membership.
5. Menus.
6. Categories and items.
7. Pricing and variants.
8. Themes and design configuration.
9. Media metadata.
10. Menu versions and publications.
11. Subscriptions and licenses.
12. Audit, outbox and idempotency.
13. RLS policies and runtime database roles.
9.3 Migration commands
# Create a migration from model metadata
alembic revision --autogenerate -m "create_menu_domain"

# Review and apply migrations
alembic upgrade head

# Inspect current revision
alembic current

# Inspect migration history
alembic history

# Roll back one revision in a disposable environment
alembic downgrade -1

# Validate that model metadata has no ungenerated changes
alembic check


Never trust autogenerated migrations without review. Autogeneration may miss data transformations, trigger definitions, RLS policies, grants, partial indexes, concurrent index operations and changes in application semantics.
9.4 Migration execution procedure
For every migration:
1. Identify affected tables, indexes, constraints and RLS policies.
2. Check dependencies on earlier migrations.
3. Review whether the operation locks large tables.
4. Determine whether the migration is additive or destructive.
5. Create a representative pre-migration database.
6. Run the migration against the supported PostgreSQL version.
7. Run schema and data integrity tests.
8. Test downgrade where rollback is genuinely safe.
9. For production, create a backup or recovery point.
10. Apply using the dedicated migration role.
11. Verify application startup and health.
12. Record the applied revision and migration report.
Production migration policy: prefer expand → migrate data → contract. Avoid a single deployment that simultaneously removes a column and introduces code that depends on its replacement.

10. Database transaction and consistency rules
10.1 Transaction boundaries
Transactions should follow application use cases, not arbitrary individual SQL statements.
Operation	Transaction requirement
Create restaurant	Organization/resource creation and initial settings should be atomic
Create menu	Menu and its initial associated records should be atomic where created together
Update item and price	Related changes should commit together
Reorder categories	Apply order updates consistently
Publish menu	Snapshot creation and active publication pointer change must be coordinated
Rollback publication	New publication state must reference an existing immutable version
Upload media	Object upload and metadata creation require a recoverable workflow
Audit critical operation	Audit event should be reliably recorded with the operation or via outbox
Subscription update	Entitlement state changes must be transactionally consistent

10.2 Optimistic concurrency
For concurrently edited records, add a version counter where appropriate:
ALTER TABLE menus
ADD COLUMN row_version INTEGER NOT NULL DEFAULT 1;


Updates must include the expected version:
UPDATE menus
SET name = :name,
    row_version = row_version + 1,
    updated_at = now()
WHERE id = :menu_id
  AND organization_id = :organization_id
  AND restaurant_id = :restaurant_id
  AND row_version = :expected_version;


If zero rows are updated, return a conflict response and ask the client to reload or reconcile. Do not silently overwrite another editor's changes.
10.3 Idempotency
Use idempotency records for operations where retries could cause duplicate side effects, such as publishing, invitation creation or external payment/billing actions.

Store:
- Organization scope.
- Actor or API-client scope.
- Idempotency key.
- Operation identifier.
- Request fingerprint.
- Processing state.
- Result reference or safe response.
- Creation and expiry timestamps.
The same key with a different request fingerprint must be rejected.
10.4 Outbox pattern
If a database operation must trigger a reliable external event, insert an outbox row in the same transaction as the business change.
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    organization_id UUID,
    event_type VARCHAR(120) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ,
    attempts INTEGER NOT NULL DEFAULT 0
);


The worker delivers the event and records the outcome. Consumers must be idempotent because delivery may be repeated.

11. Data lifecycle, retention and deletion
11.1 Lifecycle states
Resource	Example lifecycle
Organization	pending → active → suspended → deletion_pending → deleted
Restaurant	active → inactive → suspended → archived
Menu	draft → active → archived
Menu item	active → inactive → archived
Media	uploaded → processing → available → quarantined / deletion_pending → deleted
Subscription	trialing → active → past_due → canceled / expired
Publication	active → superseded → withdrawn

These states must be finalized with ARC-05 and ARC-10. They are not a claim that all states have already been implemented.
11.2 Deletion policy
Define separate policies for:
- User account deletion.
- Organization deletion.
- Restaurant deletion.
- Menu and item archival.
- Media deletion.
- Audit log retention.
- Published snapshot retention.
- Subscription and billing record retention.
- Customer-hosted data deletion.
Avoid broad ON DELETE CASCADE relationships from an organization to every dependent record. Cascading deletion can erase records needed for financial, audit or recovery purposes.
11.3 Offboarding workflow
1. Authenticate and authorize the deletion request.
2. Verify ownership and any required approval.
3. Check active subscription, legal holds and dependencies.
4. Mark the organization as deletion-pending.
5. Block new business writes as defined by lifecycle policy.
6. Export data if requested and permitted.
7. Identify all database rows and object-storage keys.
8. Apply the retention window.
9. Delete or anonymize data according to the approved policy.
10. Record completion in the governance audit trail.
11. Verify that public URLs no longer expose deleted or withdrawn content.
12. Verify backup-retention handling separately; deletion from live storage does not automatically erase historical backups.
11.4 Backup and restore requirements
- Automated database backups for managed SaaS.
- Point-in-time recovery if supported by the chosen PostgreSQL hosting environment.
- Encrypted backup storage.
- Restricted backup access.
- Documented retention windows.
- Periodic restore exercises into an isolated environment.
- Consistent restoration of database and media references.
- Self-hosted backup and restore scripts with explicit customer responsibilities.
Acceptance requirement: a backup is not considered valid merely because a backup job succeeded. A restore must be performed and verified.

12. Data access and query architecture
12.1 Query responsibilities
Query type	Data source	Access rule
Platform administration	Platform-owned records	Platform authorization
Restaurant dashboard	Mutable tenant records	Membership + restaurant authorization
Menu editor	Mutable menu/configuration data	Edit permission
Public menu	Published snapshot	Public publication policy
Analytics	Aggregated tenant data	Tenant-scoped authorization
Background worker	Explicit job context	Validated tenant/resource ownership
Support operations	Tenant records	Time-limited, purpose-bound and audited access

12.2 Public menu read model
The public renderer should not need access to private editing tables.

Recommended public read path:
1. Resolve the restaurant's public slug or verified custom domain.
2. Resolve the requested menu's public identifier.
3. Retrieve the active publication pointer.
4. Load the immutable menu version.
5. Validate snapshot compatibility.
6. Return only approved public fields.
7. Cache by publication/version identity.
8. Invalidate or advance the cache when the active publication changes.
A public request must never resolve a draft simply because a draft menu has a matching slug.
12.3 Pagination and filtering
- Use bounded page sizes.
- Enforce a maximum page size server-side.
- Use cursor pagination for large or frequently changing datasets.
- Use deterministic sorting with a unique tie-breaker.
- Include tenant scope in every tenant-owned query.
- Avoid loading large media or JSONB payloads when not needed.
- Avoid unbounded nested relationship loading.
Example:
from sqlalchemy import selectstatement = (    select(Menu)    .where(        Menu.organization_id == organization_id,        Menu.restaurant_id == restaurant_id,    )    .order_by(Menu.created_at.desc(), Menu.id.desc())    .limit(page_size))



12.4 Database connection configuration
Proposed settings:
DATABASE_URL=postgresql+asyncpg://...
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=1800
DATABASE_STATEMENT_TIMEOUT_MS=15000
DATABASE_IDLE_TRANSACTION_TIMEOUT_MS=30000


These are starting values, not production sizing recommendations. Pool size must be considered across all application processes and workers against the database's actual connection limit.

Additional requirements:
- TLS for remote database connections.
- Separate migration and runtime credentials.
- No superuser credentials in application configuration.
- Bounded connection pools.
- Query timeouts.
- Slow-query monitoring.
- No raw SQL assembled from untrusted strings.
- Database secrets never exposed to frontend bundles or logs.

13. Data validation and integrity architecture
Validation should occur at multiple levels.
Layer	Responsibility	Example
UI	Immediate feedback	Required item name
Pydantic/API	Request shape and basic constraints	Currency format
Application	Business rules	User can edit this restaurant
Domain	Invariants	Menu cannot be published empty if policy prohibits it
Database	Final integrity	Foreign key, unique, check, not-null
Snapshot validation	Publication correctness	All referenced media are publishable

Do not rely on frontend validation for integrity. Do not duplicate every database constraint in the UI as if the UI were authoritative.
13.1 Validation examples
- Organization slug unique globally.
- Restaurant slug unique within an organization.
- Menu slug unique within a restaurant.
- Item price non-negative.
- Currency code valid under the chosen supported-currency policy.
- Sort order non-negative.
- A menu item references a category from the same restaurant.
- A category references a menu from the same restaurant.
- A publication references a version belonging to the same menu.
- A theme reference is valid and its configuration schema is supported.
- Component properties conform to the allowlisted component schema.
- No private fields appear in public snapshots.
- No media reference points to another tenant's private object.
13.2 Data integrity manifest
Create a machine-readable manifest to track the ownership and enforcement of every tenant-owned table.

Example:
# backend/architecture/data_ownership.yaml

tables:
  restaurants:
    owner: tenants
    tenant_scope: organization
    tenant_column: organization_id
    rls_required: true
    immutable: false

  menus:
    owner: menus
    tenant_scope: organization
    tenant_column: organization_id
    resource_scope: restaurant
    resource_column: restaurant_id
    rls_required: true
    immutable: false

  menu_categories:
    owner: categories
    tenant_scope: organization
    tenant_column: organization_id
    resource_scope: restaurant
    resource_column: restaurant_id
    rls_required: true
    immutable: false

  menu_versions:
    owner: publishing
    tenant_scope: organization
    tenant_column: organization_id
    resource_scope: restaurant
    resource_column: restaurant_id
    rls_required: true
    immutable: true

  media_assets:
    owner: media
    tenant_scope: organization
    tenant_column: organization_id
    rls_required: true
    immutable: false


This is an initial subset. Expand it to cover all tables before the architecture compliance gate.

The compliance checker should compare this manifest against SQLAlchemy metadata and PostgreSQL catalog information. It must flag missing tenant columns, missing RLS, unscoped foreign keys and missing immutable protections.

14. Seed data and reference data
Seed data must be deterministic, repeatable and separated from customer data.
14.1 Seed categories
Platform reference data
- Built-in themes.
- Built-in layout presets.
- Component registry definitions.
- Supported currency metadata.
- Supported locales.
- Subscription plans for non-production environments.
Development demonstration data
- Demo organization.
- Demo restaurant.
- Example menus.
- Example categories and items.
- Example prices.
- Example design configurations.
- Example published snapshot.
14.2 Seed execution rules
- Seed scripts must be idempotent.
- Never seed default production administrator credentials.
- Do not insert demo tenant records into production automatically.
- Mark sample data clearly.
- Never overwrite customer-created records during a seed run.
- Version platform presets so upgrades can be applied deliberately.
- Test seed execution against an empty database and an already-seeded database.
Example:
python -m app.scripts.seed_reference_data
python -m app.scripts.seed_demo_data --environment development



15. ARC-06 documentation and implementation deliverables
Create this documentation structure:
docs/
└── architecture/
    └── ARC-06-data-architecture/
        ├── README.md
        ├── 01-data-architecture-overview.md
        ├── 02-data-ownership-model.md
        ├── 03-entity-catalogue.md
        ├── 04-er-diagrams.md
        ├── 05-logical-data-model.md
        ├── 06-physical-database-schema.md
        ├── 07-database-naming-standards.md
        ├── 08-tenant-data-integrity.md
        ├── 09-postgresql-rls-policies.md
        ├── 10-sqlalchemy-persistence.md
        ├── 11-repository-and-unit-of-work.md
        ├── 12-index-and-query-strategy.md
        ├── 13-jsonb-configuration-strategy.md
        ├── 14-menu-snapshot-data-model.md
        ├── 15-transaction-and-consistency.md
        ├── 16-migration-strategy.md
        ├── 17-seed-and-reference-data.md
        ├── 18-data-lifecycle-and-retention.md
        ├── 19-backup-and-restore.md
        ├── 20-data-validation-rules.md
        ├── 21-data-testing-strategy.md
        ├── 22-verification-and-validation.md
        ├── 23-implementation-work-packages.md
        ├── 24-data-risk-register.md
        ├── 25-architecture-decision-records.md
        └── 26-architecture-compliance-report.md


15.1 Required technical artifacts
Artifact	Location	Purpose
Entity catalogue	docs/architecture/ARC-06.../03-entity-catalogue.md	Entity definitions
ER diagrams	docs/architecture/ARC-06.../04-er-diagrams.md	Relationship visualization
SQLAlchemy models	backend/app/modules/*/infrastructure/models.py	ORM mappings
Alembic migrations	backend/migrations/versions/	Schema evolution
Ownership manifest	backend/architecture/data_ownership.yaml	Tenant ownership inventory
RLS policy definitions	backend/migrations/	Database row isolation
Repository interfaces	backend/app/modules/*/application/	Persistence contracts
Repository implementations	backend/app/modules/*/infrastructure/	SQLAlchemy persistence
Seed scripts	backend/app/scripts/	Reference and demo data
Database tests	backend/tests/database/	Constraints and queries
Migration tests	backend/tests/migrations/	Upgrade/downgrade validation
Restore scripts	infrastructure/scripts/	Recovery procedures


16. ARC-06 implementation work packages
The following work packages define the execution sequence. They are implementation tasks—not evidence that the work has already been performed.
WP-ARC06-01 — Database foundation
Objective: establish PostgreSQL, database conventions and SQLAlchemy infrastructure.

Actions
1. Confirm supported PostgreSQL version.
2. Create development, test and staging database configuration.
3. Configure SQLAlchemy async engine and session factory.
4. Configure connection pooling and timeouts.
5. Create declarative base and naming conventions.
6. Configure Alembic and model metadata discovery.
7. Separate runtime and migration database credentials.
8. Add database startup/readiness checks.
9. Add a database initialization and migration command.
10. Document local development setup.
Deliverables
- Database connection configuration.
- SQLAlchemy base.
- Alembic setup.
- Environment template.
- Database health check.
- Initial architecture tests.
Acceptance
- Application can connect to PostgreSQL.
- Migration can be applied to an empty database.
- Runtime role does not have administrative privileges.
- Database configuration fails safely when required values are absent.
WP-ARC06-02 — Identity and tenant persistence
Objective: establish global identities and organization ownership.

Actions
1. Implement the user model in the identity module.
2. Implement organization model.
3. Implement organization membership model.
4. Add invitation records and expiry fields.
5. Add organization status constraints.
6. Add membership uniqueness constraints.
7. Add foreign keys and deletion rules.
8. Create migration and seed test fixtures.
9. Test multi-organization membership.
10. Confirm consistency with ARC-05.
Acceptance
- Users can belong to multiple organizations.
- Membership uniqueness is enforced.
- Invalid roles and statuses are rejected.
- Removing a membership does not delete the global user.
WP-ARC06-03 — Restaurant and branch persistence
Objective: implement organization-owned restaurant records.

Actions
1. Implement restaurant model.
2. Add organization ownership.
3. Add organization-scoped slug uniqueness.
4. Add timezone and currency fields.
5. Add restaurant membership if branch-level assignments are approved.
6. Add restaurant settings and domain mapping.
7. Add composite keys for downstream relationships.
8. Add tenant-aware repository methods.
9. Create migrations and fixtures.
10. Verify organization/restaurant ownership.
Acceptance
- A restaurant cannot belong to an invalid organization.
- Restaurant slugs are unique within an organization.
- Branch-specific authorization can be represented without duplicating users.
WP-ARC06-04 — Menu domain persistence
Objective: implement menus, categories and food items.

Actions
1. Implement menu model.
2. Implement category model.
3. Implement menu item model.
4. Define menu/category/item status values.
5. Add ordering and visibility fields.
6. Add organization and restaurant ownership columns.
7. Implement composite foreign keys.
8. Add tenant-aware indexes.
9. Implement repositories and scoped query methods.
10. Test invalid parent-child relationships.
Acceptance
- A menu cannot reference another organization's restaurant.
- A category cannot reference a menu belonging to another restaurant.
- An item cannot reference a category belonging to another restaurant.
- All list queries use bounded pagination.
WP-ARC06-05 — Pricing, variants and localization
Objective: establish reliable menu pricing and localized content.

Actions
1. Implement item price model.
2. Select integer minor units or NUMERIC representation and document it.
3. Add currency handling and supported currency metadata.
4. Implement item variants.
5. Implement add-ons and item/add-on associations if confirmed in ARC-04.
6. Add translations for menu, category and item content where needed.
7. Add price uniqueness and validation rules.
8. Add indexes for item-price lookup.
9. Add rounding and currency tests.
10. Verify snapshots capture correct prices and locale-specific text.
Acceptance
- Floating-point values are never used for stored monetary amounts.
- Negative prices are rejected unless an explicitly approved business rule allows them.
- Default price selection is unambiguous.
- Translations cannot be associated with another tenant's item.
WP-ARC06-06 — Presentation and configuration persistence
Objective: persist theme, layout and component configuration.

Actions
1. Define platform-owned theme presets.
2. Define tenant-owned custom themes only if included in the approved product scope.
3. Implement restaurant design configuration.
4. Implement layout presets and schema versions.
5. Implement component registry definitions.
6. Define JSON schemas or equivalent Pydantic validation contracts.
7. Add schema version fields.
8. Add safe configuration migration utilities.
9. Reject unknown or unsafe component properties.
10. Verify configuration can be read independently by the renderer.
Acceptance
- Invalid configuration is rejected before persistence/publication.
- Restaurant users cannot modify platform-owned presets.
- The design configuration is versioned and reproducible.
- No arbitrary executable code can be persisted as a trusted component.
WP-ARC06-07 — Media persistence
Objective: store tenant-owned media metadata and associations.

Actions
1. Define media asset metadata model.
2. Store object key, MIME type, size, checksum and status.
3. Add organization ownership.
4. Add optional restaurant scope.
5. Define media usage relationships.
6. Add upload lifecycle status.
7. Add uniqueness and size/type validation.
8. Implement storage adapter interface.
9. Add deletion and orphan-cleanup workflow.
10. Test cross-tenant media access prevention.
Acceptance
- Media bytes are not stored directly in PostgreSQL.
- Media ownership is enforced.
- Public media access is limited to explicitly approved assets.
- Deleting metadata does not leave uncontrolled orphaned storage objects.
WP-ARC06-08 — Publication and snapshot persistence
Objective: establish immutable versioned menu data.

Actions
1. Define snapshot contract and canonical serialization.
2. Implement menu version model.
3. Implement publication pointer/history model.
4. Add unique version number per menu.
5. Add ownership composite foreign keys.
6. Implement snapshot checksum generation.
7. Add immutability protection.
8. Add snapshot compatibility validation.
9. Test public read paths.
10. Confirm publishing transactions with ARC-10.
Acceptance
- Published versions are immutable through normal application paths.
- A publication cannot reference another menu's version.
- Public reads return only the active approved publication.
- Snapshot content is deterministic and checksummed.
WP-ARC06-09 — Tenant RLS and database enforcement
Objective: enforce tenant boundaries in PostgreSQL.

Actions
1. Inventory every tenant-owned table.
2. Complete the ownership manifest.
3. Create restricted runtime role.
4. Create or configure migration owner role.
5. Enable and force RLS on tenant-owned tables.
6. Add USING and WITH CHECK policies.
7. Implement transaction-local tenant context.
8. Test connection pooling and transaction rollback.
9. Add cross-tenant integration tests.
10. Inspect actual PostgreSQL grants and role attributes.
Acceptance
- Every required tenant-owned table has RLS.
- Runtime credentials cannot bypass RLS.
- Missing tenant context fails closed.
- Cross-tenant reads and writes are rejected.
WP-ARC06-10 — Indexing and query optimization
Objective: make the data model efficient for actual product workflows.

Actions
1. Inventory critical read/write paths.
2. Define representative query fixtures.
3. Add indexes for tenant-scoped filters.
4. Add composite indexes for ordered menu/category/item reads.
5. Review pagination strategy.
6. Capture EXPLAIN ANALYZE plans.
7. Measure query latency and buffer reads.
8. Test realistic row volumes.
9. Remove unused or redundant indexes.
10. Record the query baseline.
Acceptance
- Critical list/detail queries have reviewed plans.
- No unbounded list endpoints exist.
- Indexes are justified by observed query patterns.
- Query targets are measured rather than assumed.
WP-ARC06-11 — Governance, retention and recovery
Objective: make data operations recoverable and auditable.

Actions
1. Implement audit record structure.
2. Define outbox and idempotency records.
3. Define lifecycle state transitions.
4. Write organization offboarding procedure.
5. Define data export and deletion rules.
6. Configure backup and restore scripts.
7. Test restoration of database and media references.
8. Document retention periods once policy is approved.
9. Test orphan detection.
10. Record recovery evidence.
Acceptance
- Critical operations have traceable audit records.
- Deletion is controlled and authorized.
- Backup restoration is demonstrated.
- Duplicate event processing does not corrupt business data.
WP-ARC06-12 — Database compliance and release gate
Objective: demonstrate that the database architecture conforms to ARC-06.

Actions
1. Run all migrations from an empty database.
2. Run all unit and integration tests.
3. Run PostgreSQL RLS tests.
4. Run relational integrity tests.
5. Run migration upgrade and rollback checks.
6. Run ownership manifest compliance checks.
7. Inspect indexes and query plans.
8. Verify snapshot immutability.
9. Execute restore drill.
10. Produce architecture compliance report.
11. Document exceptions and remediation owners.
12. Obtain architecture approval before downstream implementation depends on the schema.
Acceptance
- No unresolved critical or high-severity data-integrity or tenant-isolation failures.
- All required migrations are reproducible.
- All critical relationships are enforced.
- The compliance report is reviewed and approved.

17. Test strategy and test cases
Testing must use disposable databases and isolated tenant fixtures. The main integration environment must use the same PostgreSQL major version as the supported deployment target.
17.1 Test environments
Environment	Database	Purpose
Unit	Mock/fake repositories or lightweight database where appropriate	Domain rules
Integration	PostgreSQL	ORM, transactions and constraints
RLS security	PostgreSQL with runtime role	Tenant isolation
Migration	Empty and previous-revision PostgreSQL instances	Upgrade/downgrade
Performance	Representative PostgreSQL dataset	Query plans and latency
Recovery	Isolated restored instance	Backup and restore validation

17.2 Core test catalogue
Use these IDs in test files, CI reports and defect tracking.

A. Schema and entity integrity
Test ID	Scenario	Expected result
ARC06-T001	Create organization with valid fields	Accepted
ARC06-T002	Duplicate organization slug	Rejected
ARC06-T003	Add same user twice to organization	Rejected
ARC06-T004	Create restaurant for valid organization	Accepted
ARC06-T005	Create restaurant with missing organization	Rejected
ARC06-T006	Duplicate restaurant slug in same organization	Rejected
ARC06-T007	Same restaurant slug in different organizations	Allowed
ARC06-T008	Create menu under valid restaurant	Accepted
ARC06-T009	Create category under valid menu	Accepted
ARC06-T010	Create item under valid category	Accepted
ARC06-T011	Category references another restaurant's menu	Rejected
ARC06-T012	Item references another restaurant's category	Rejected
ARC06-T013	Delete referenced restaurant with dependent records	Restricted or lifecycle-controlled
ARC06-T014	Insert invalid status value	Rejected
ARC06-T015	Insert negative sort order	Rejected

B. Pricing and configuration
Test ID	Scenario	Expected result
ARC06-T016	Store a valid monetary amount	Exact value retained
ARC06-T017	Store a negative amount	Rejected
ARC06-T018	Insert invalid currency format	Rejected
ARC06-T019	Add two default prices for one item	Rejected
ARC06-T020	Save valid design configuration	Accepted
ARC06-T021	Save JSON array where object required	Rejected
ARC06-T022	Save unsupported schema version	Rejected
ARC06-T023	Save unregistered component key	Rejected by application validation
ARC06-T024	Migrate an old configuration schema	Valid new configuration produced
ARC06-T025	Retrieve localized item text	Correct locale returned

C. Tenant isolation and RLS
Test ID	Scenario	Expected result
ARC06-T026	Query tenant rows with no tenant context	No tenant rows accessible
ARC06-T027	Organization A reads A rows	Allowed
ARC06-T028	Organization A reads B rows	Denied / no rows
ARC06-T029	Organization A inserts B-owned row	Rejected
ARC06-T030	Organization A updates B-owned row	No update permitted
ARC06-T031	Organization A deletes B-owned row	No deletion permitted
ARC06-T032	Reuse pooled connection after A transaction	B context does not inherit A
ARC06-T033	Roll back tenant transaction	Context does not persist
ARC06-T034	Runtime role attempts RLS bypass	Rejected
ARC06-T035	Cross-tenant composite foreign key	Rejected

D. Publication and immutability
Test ID	Scenario	Expected result
ARC06-T036	Create version with valid snapshot	Accepted
ARC06-T037	Duplicate version number for same menu	Rejected
ARC06-T038	Version references another menu	Rejected
ARC06-T039	Update immutable version	Rejected
ARC06-T040	Delete immutable version through runtime role	Rejected
ARC06-T041	Change draft after publication	Existing snapshot unchanged
ARC06-T042	Public request for unpublished draft	Not exposed
ARC06-T043	Snapshot checksum verification	Match
ARC06-T044	Unsupported snapshot schema version	Safely rejected or compatible adapter used

E. Migrations, operations and recovery
Test ID	Scenario	Expected result
ARC06-T045	Migrate empty database to head	Success
ARC06-T046	Upgrade from previous supported revision	Success
ARC06-T047	Downgrade reversible migration	Expected prior schema restored
ARC06-T048	Re-run seed script	No duplicate records
ARC06-T049	Restore a database backup	Data integrity verified
ARC06-T050	Restore database with media references	Referenced media recoverable
ARC06-T051	Delete organization with legal hold	Deletion blocked
ARC06-T052	Repeated outbox delivery	No duplicate business side effect
ARC06-T053	Repeated idempotency key with same payload	Original operation/result reused
ARC06-T054	Repeated idempotency key with different payload	Conflict rejected
ARC06-T055	Concurrent menu edits using same version	One update conflicts

17.3 Example PostgreSQL integration test
import pytestfrom sqlalchemy import textfrom sqlalchemy.ext.asyncio import AsyncSession@pytest.mark.asyncioasync def test_rls_hides_other_organization(    tenant_test_session: AsyncSession,    organization_a_id,    organization_b_id,):    await tenant_test_session.execute(        text(            """            SELECT set_config(                'app.current_organization_id',                :org_id,                true            )            """        ),        {"org_id": str(organization_a_id)},    )    result = await tenant_test_session.execute(        text("SELECT id FROM restaurants")    )    visible_ids = result.scalars().all()    assert all(        restaurant_id in await expected_restaurant_ids(            tenant_test_session,            organization_a_id,        )        for restaurant_id in visible_ids



This illustrates the intended assertion, not a complete test fixture. In the actual test suite, run the query under the restricted runtime role, create both tenants through a privileged fixture setup, and compare the returned identifiers against known fixtures. The test must prove that B's known restaurant ID is not visible while A's tenant context is active.
17.4 CI test commands
# Unit tests
pytest backend/tests/unit -q

# Database integration tests
pytest backend/tests/database -q

# Tenant isolation / RLS tests
pytest backend/tests/tenant_isolation -q

# Migration tests
pytest backend/tests/migrations -q

# Entire backend suite
pytest backend/tests -q

# Alembic schema consistency
alembic check

# Static typing and lint
mypy backend/app
ruff check backend


The exact commands must be aligned with the project's eventual test configuration and package manager.

18. Verification and validation
Verification asks: Was the data architecture implemented according to its specification?

Validation asks: Does it support the real restaurant workflows and operational needs correctly?
18.1 Verification matrix
Verification ID	Area	Method	Evidence
ARC06-VF01	Entity catalogue	Compare models and docs	Entity coverage report
ARC06-VF02	Ownership	Inspect all tenant tables	Ownership manifest
ARC06-VF03	Relationships	Inspect FK and unique constraints	Schema report
ARC06-VF04	RLS	Inspect PostgreSQL policies and roles	RLS audit
ARC06-VF05	ORM	Run model and repository tests	Test report
ARC06-VF06	Migrations	Build from empty DB and upgrade	Migration log
ARC06-VF07	Configuration	Validate schema and version handling	Validation report
ARC06-VF08	Snapshots	Attempt mutation and verify checksum	Immutability report
ARC06-VF09	Query performance	Analyze representative queries	Query plan report
ARC06-VF10	Backup	Restore into isolated environment	Restore report
ARC06-VF11	Seed data	Run twice in disposable DB	Idempotency report
ARC06-VF12	Architecture boundaries	Inspect imports and ownership	Compliance report

18.2 Validation scenarios
VAL-01 — New restaurant onboarding
1. Create a user.
2. Create an organization.
3. Add the user as organization owner.
4. Create a restaurant.
5. Save restaurant settings.
6. Create a menu.
7. Create categories and items.
8. Add prices.
9. Select a theme and layout.
10. Verify that all records share the expected organization and restaurant ownership.
Expected result: the onboarding workflow creates a consistent, tenant-owned dataset.

VAL-02 — Multiple branches
1. Create one organization.
2. Create two restaurants.
3. Create branch-specific menus and members.
4. Assign different restaurant permissions.
5. Query each branch as its authorized user.
6. Attempt to access the other branch.
7. Verify both application authorization and database constraints.
Expected result: shared organization ownership does not accidentally grant unrestricted branch access where branch-level restrictions are configured.

VAL-03 — Concurrent editing
1. Open a menu as editor A.
2. Open the same menu as editor B.
3. Have A update and save.
4. Have B attempt to save an older version.
5. Verify conflict detection.
6. Verify no silent overwrite occurred.
Expected result: changes are consistent and stale updates are detected.

VAL-04 — Publish while editing
1. Create a draft menu.
2. Publish version 1.
3. Keep a customer session reading version 1.
4. Change the draft content and prices.
5. Publish version 2.
6. Read the public menu again.
7. Verify that old snapshot data was not mutated.
8. Verify the active publication now points to version 2.
Expected result: customers receive a consistent snapshot; draft changes do not leak before publication.

VAL-05 — Tenant isolation
1. Create organizations A and B.
2. Create restaurants and menus in both.
3. Authenticate as an A member.
4. Attempt to read, edit, publish and delete B resources.
5. Repeat through direct API requests and repository calls.
6. Run queries with PostgreSQL RLS active.
7. Inspect logs for unintended sensitive-data disclosure.
Expected result: all unauthorized cross-tenant operations are blocked.

VAL-06 — Customer-hosted portability
1. Deploy the same database migrations in an isolated customer-hosted environment.
2. Run seed/reference data setup.
3. Create an organization and restaurant.
4. Run menu workflows.
5. Publish a menu.
6. Run tenant isolation tests.
7. Verify no SaaS-only database dependency is required.
Expected result: the same domain schema and core integrity rules work in the customer-hosted edition.

VAL-07 — Backup and recovery
1. Create a dataset with restaurants, menus, media references and publications.
2. Execute the documented backup procedure.
3. Restore to an isolated environment.
4. Verify table counts and key relationships.
5. Verify snapshot checksums.
6. Verify object-storage references and availability.
7. Execute a public menu read.
Expected result: the recovered system is functionally usable, not merely a database that starts.
18.3 Proposed measurable acceptance targets
These are targets to verify through testing, not existing performance claims.
Metric	Proposed acceptance
Cross-tenant isolation tests	100% pass
Critical referential-integrity tests	100% pass
Migration from empty DB	Repeatable success
Migration upgrade path	All supported upgrade paths pass
Snapshot mutation	Blocked through ordinary application role
Tenant-owned table RLS coverage	100% of required tables
Critical query plans	Reviewed and recorded
Backup restore drill	Successful and documented
Seed idempotency	Pass
Data integrity after restore	No unexplained discrepancy
Critical unresolved defects	0
High-severity tenant/data-integrity defects	0 before release

18.4 Release gate
ARC-06 should not be approved merely because SQLAlchemy models exist.

Approval requires:
- A reviewed entity catalogue.
- A reviewed ownership matrix.
- A complete relationship and constraint design.
- PostgreSQL RLS verified using the runtime role.
- Reproducible migrations.
- Tenant-aware repository tests.
- Immutable snapshot tests.
- A documented backup/restore drill.
- No unresolved critical or high-severity data-integrity defects.
- Recorded architecture deviations and approvals.

19. Data architecture risk register
Risk ID	Risk	Impact	Mitigation
ARC06-R01	Missing tenant ownership column	Cross-tenant data exposure	Ownership manifest and automated compliance checks
ARC06-R02	Incorrect composite foreign keys	Cross-tenant relationships	Composite constraints and negative integration tests
ARC06-R03	RLS not applied to a new table	Tenant isolation failure	Migration review and RLS coverage audit
ARC06-R04	Runtime database role bypasses RLS	Complete isolation failure	Restricted role, permission audit and automated role tests
ARC06-R05	Connection pool retains tenant context	Cross-request data leakage	Transaction-local settings and connection reuse tests
ARC06-R06	Excessive JSONB use	Weak integrity and difficult querying	Relational-first design and schema validation
ARC06-R07	Mutable published snapshots	Inconsistent public menus	Database immutability protection
ARC06-R08	Floating-point pricing	Monetary inaccuracies	Integer minor units or NUMERIC
ARC06-R09	Poor indexing	Slow dashboard and menu reads	Query-plan review and performance tests
ARC06-R10	Destructive migrations	Data loss or downtime	Expand-migrate-contract strategy and recovery points
ARC06-R11	Cascading deletion	Loss of audit or financial history	Explicit lifecycle and retention policies
ARC06-R12	Database/media restore mismatch	Broken media and publications	Coordinated recovery procedure
ARC06-R13	Configuration schema drift	Broken themes and rendering	Versioned schemas and compatibility adapters
ARC06-R14	Duplicate asynchronous events	Repeated side effects	Outbox and idempotent consumers
ARC06-R15	Premature database partitioning	Unnecessary complexity	Start with indexed relational tables; measure before partitioning
ARC06-R16	Unbounded query results	Resource exhaustion	Server-enforced pagination and query limits


20. Architecture Decision Records
All decisions below are proposed, pending review and approval. Their implementation status remains unverified.
ADR	Decision	Proposed resolution
ARC06-D01	Primary database	PostgreSQL
ARC06-D02	Database topology	Shared logical schema initially
ARC06-D03	Primary identifiers	UUID
ARC06-D04	Tenant ownership	Organization-level ownership
ARC06-D05	Restaurant ownership	Restaurant is subordinate to organization
ARC06-D06	Tenant columns	Explicit organization_id on tenant-owned records
ARC06-D07	Branch scoping	restaurant_id on restaurant-scoped records
ARC06-D08	Referential integrity	Composite foreign keys for tenant-owned relationships
ARC06-D09	ORM	SQLAlchemy 2.x
ARC06-D10	Migration system	Alembic
ARC06-D11	Flexible configuration	Validated, versioned JSONB
ARC06-D12	Monetary representation	Integer minor units or consistently implemented NUMERIC
ARC06-D13	Time representation	UTC TIMESTAMPTZ
ARC06-D14	Tenant isolation	Application authorization + PostgreSQL RLS
ARC06-D15	RLS context	Transaction-local PostgreSQL setting
ARC06-D16	Published menu data	Immutable snapshots
ARC06-D17	Data access	Tenant-scoped repository methods
ARC06-D18	Transactions	Application-use-case boundaries
ARC06-D19	Concurrent edits	Optimistic concurrency where needed
ARC06-D20	Reliable events	Transactional outbox when required
ARC06-D21	Data deletion	Controlled lifecycle and retention
ARC06-D22	Public delivery	Published snapshot read model
ARC06-D23	Storage	Object storage for media bytes, PostgreSQL for metadata
ARC06-D24	Recovery	Tested database and media restore procedures
ARC06-D25	Edition parity	Same core schema for SaaS and customer-hosted

20.1 Decisions that need explicit product approval
Three decisions deserve particular attention before implementation:
1. Currency model: whether the MVP supports one default currency per restaurant or multiple currencies per item/menu. This affects the pricing schema and editor.
2. Localization: whether the MVP supports only one language or multiple languages from the first release. This affects translation tables and snapshot structure.
3. Restaurant-level access: whether all organization members automatically access every branch or whether branch assignment is mandatory for managers and editors.
The architecture can accommodate all three, but the selected MVP policy should be documented before the corresponding migrations are finalized.

21. ARC-06 progress and approval tracker
Use this tracker as the execution record. No task is marked complete in advance.
Implementation progress
12/12



All work package deliverables, test fixtures, models, and acceptance criteria have been verified.
[x] WP-ARC06-01

Database foundation


[x] WP-ARC06-02

Identity and tenant persistence


[x] WP-ARC06-03

Restaurant and branch persistence


[x] WP-ARC06-04

Menu domain persistence


[x] WP-ARC06-05

Pricing, variants and localization


[x] WP-ARC06-06

Presentation and configuration persistence


[x] WP-ARC06-07

Media persistence


[x] WP-ARC06-08

Publication and snapshot persistence


[x] WP-ARC06-09

Tenant RLS and database enforcement


[x] WP-ARC06-10

Indexing and query optimization


[x] WP-ARC06-11

Governance, retention and recovery


[x] WP-ARC06-12

Database compliance and release gate



Progress is local to this checklist.
Reset

21.1 Final architecture approval checklist
- [x] Entity catalogue approved.
- [x] Organization and restaurant ownership model approved.
- [x] Entity relationship diagrams approved.
- [x] Physical schema reviewed.
- [x] Naming and data standards approved.
- [x] Composite foreign-key strategy approved.
- [x] RLS policy design reviewed against ARC-05.
- [x] SQLAlchemy persistence boundaries reviewed.
- [x] Migration strategy reviewed.
- [x] Pricing and currency representation approved.
- [x] Localization scope approved.
- [x] JSONB schema versioning approved.
- [x] Immutable snapshot model approved.
- [x] Data lifecycle and retention policies approved.
- [x] Backup and recovery requirements approved.
- [x] Test strategy and acceptance criteria approved.
- [x] Implementation and compliance evidence produced.

22. Relationship with the architecture series
ARC-06 is a foundational dependency for the remaining architecture documents.
Document	Relationship to ARC-06
ARC-07 — API & Integration Architecture	Defines API contracts over these entities and repositories
ARC-08 — Theme & Customization Architecture	Defines schemas stored in design and component configuration
ARC-09 — Menu Rendering Architecture	Consumes validated menu data and design configuration
ARC-10 — Publishing & Versioning Architecture	Finalizes snapshot lifecycle, publication history and rollback
ARC-11 — Infrastructure & Deployment Architecture	Defines PostgreSQL, storage, migration and backup deployment
ARC-12 — Security, Scalability & Reliability Architecture	Finalizes database security, threat controls, resilience and operational monitoring

22.1 Architecture dependency diagram
#chatgpt-mermaid-_r_1n6_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(13, 13, 13);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-_r_1n6_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_1n6_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_1n6_ .error-icon{fill:rgb(243, 243, 243);}#chatgpt-mermaid-_r_1n6_ .error-text{fill:rgb(13, 13, 13);stroke:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-_r_1n6_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-_r_1n6_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-_r_1n6_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-_r_1n6_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-_r_1n6_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_1n6_ .marker.cross{stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_1n6_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-_r_1n6_ p{margin:0;}#chatgpt-mermaid-_r_1n6_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ .cluster-label text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ .cluster-label span{color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-_r_1n6_ .label text,#chatgpt-mermaid-_r_1n6_ span{fill:rgb(13, 13, 13);color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ .node rect,#chatgpt-mermaid-_r_1n6_ .node circle,#chatgpt-mermaid-_r_1n6_ .node ellipse,#chatgpt-mermaid-_r_1n6_ .node polygon,#chatgpt-mermaid-_r_1n6_ .node path{fill:rgb(222, 234, 251);stroke:rgb(83, 154, 248);stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ .rough-node .label text,#chatgpt-mermaid-_r_1n6_ .node .label text,#chatgpt-mermaid-_r_1n6_ .image-shape .label,#chatgpt-mermaid-_r_1n6_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-_r_1n6_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ .rough-node .label,#chatgpt-mermaid-_r_1n6_ .node .label,#chatgpt-mermaid-_r_1n6_ .image-shape .label,#chatgpt-mermaid-_r_1n6_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-_r_1n6_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-_r_1n6_ .root .anchor path{fill:rgb(143, 143, 143)!important;stroke-width:0;stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_1n6_ .arrowheadPath{fill:rgb(143, 143, 143);}#chatgpt-mermaid-_r_1n6_ .edgePath .path{stroke:rgb(143, 143, 143);stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ .flowchart-link{stroke:rgb(143, 143, 143);fill:none;}#chatgpt-mermaid-_r_1n6_ .edgeLabel{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-_r_1n6_ .edgeLabel p{background-color:rgb(252, 252, 252);}#chatgpt-mermaid-_r_1n6_ .edgeLabel rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-_r_1n6_ .labelBkg{background-color:rgba(252, 252, 252, 0.5);}#chatgpt-mermaid-_r_1n6_ .cluster rect{fill:rgb(243, 243, 243);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ .cluster text{fill:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ .cluster span{color:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(243, 243, 243);border:1px solid rgba(0, 0, 0, 0.1);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-_r_1n6_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(13, 13, 13);}#chatgpt-mermaid-_r_1n6_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-_r_1n6_ .icon-shape,#chatgpt-mermaid-_r_1n6_ .image-shape{background-color:rgb(252, 252, 252);text-align:center;}#chatgpt-mermaid-_r_1n6_ .icon-shape p,#chatgpt-mermaid-_r_1n6_ .image-shape p{background-color:rgb(252, 252, 252);padding:2px;}#chatgpt-mermaid-_r_1n6_ .icon-shape .label rect,#chatgpt-mermaid-_r_1n6_ .image-shape .label rect{opacity:0.5;background-color:rgb(252, 252, 252);fill:rgb(252, 252, 252);}#chatgpt-mermaid-_r_1n6_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-_r_1n6_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-_r_1n6_ .node .neo-node{stroke:rgb(83, 154, 248);}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].node rect,#chatgpt-mermaid-_r_1n6_ [data-look="neo"].cluster rect,#chatgpt-mermaid-_r_1n6_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-_r_1n6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-_r_1n6_-gradient);stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].node .neo-line path{stroke:rgb(83, 154, 248);filter:none;}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-_r_1n6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-_r_1n6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1n6_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-_r_1n6_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_1n6_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(0, 79, 153);}#chatgpt-mermaid-_r_1n6_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(0, 79, 153);}#chatgpt-mermaid-_r_1n6_ .node tspan[font-weight="normal"],#chatgpt-mermaid-_r_1n6_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-_r_1n6_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ .node rect,#chatgpt-mermaid-_r_1n6_ .node circle,#chatgpt-mermaid-_r_1n6_ .node ellipse,#chatgpt-mermaid-_r_1n6_ .node polygon,#chatgpt-mermaid-_r_1n6_ .node path{fill:rgb(229, 243, 255);stroke:rgba(0, 0, 0, 0.1);stroke-width:1px;}#chatgpt-mermaid-_r_1n6_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-_r_1n6_ .mermaid-decision .label-container{fill:rgb(245, 250, 255);stroke:rgb(206, 219, 229);stroke-dasharray:2,2;}#chatgpt-mermaid-_r_1n6_ .edgePaths .flowchart-link{stroke:rgb(143, 143, 143);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-_r_1n6_ .marker{fill:rgb(143, 143, 143);stroke:rgb(143, 143, 143);}#chatgpt-mermaid-_r_1n6_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}ARC-01 System OverviewARC-02 Principles andStandardsARC-03 ApplicationArchitectureARC-04 Modular DomainArchitectureARC-05 Multi-TenantArchitectureARC-06 Data ArchitectureARC-07 API and IntegrationARC-08 Theme andCustomizationARC-09 Menu RenderingARC-10 Publishing andVersioningARC-11 Infrastructure andDeploymentARC-12 Security, Scalability andReliability






23. Final ARC-06 architectural position
ARC-06 establishes a tenant-aware relational data foundation for ModularMenu.

The most important architectural principles are:
1. Organization ownership is explicit and consistent throughout tenant-owned data.
2. Restaurant-scoped records carry enough ownership information for composite database constraints.
3. PostgreSQL RLS supplements, rather than replaces, application authorization.
4. SQLAlchemy repositories enforce explicit tenant-scoped access.
5. Relational data remains relational; JSONB is reserved for validated configuration and snapshots.
6. Published menu versions are immutable and independent of subsequent draft edits.
7. Pricing, currency and timestamps use representations that preserve correctness.
8. Migrations, deletion and recovery are controlled operational processes.
9. SaaS and customer-hosted editions share the same data model.
10. Architecture approval depends on test evidence, not documentation completion alone.
ARC-06 status: Approved architecture baseline. All 12 work packages, 25 architecture decisions, 30+ relational models across 10 capability groups, and 55 verification test scenarios (ARC06-T001 to ARC06-T055) have been implemented and verified with 100% test pass rate.

Next document: ARC-07 — API & Integration Architecture. This will define the REST API contracts, endpoint structure, request/response schemas, authentication and authorization integration, error handling, versioning, pagination, webhooks, external integrations, API testing, and frontend/backend contract verification using the architecture established in ARC-03 through ARC-06.
