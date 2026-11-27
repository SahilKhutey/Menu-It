"""establish organization tenant foundation (FCD-04 §6.3, §7, §12)

Revision ID: 0002_org_foundation
Revises: 0001_initial_tables
Create Date: 2026-11-24 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_org_foundation"
down_revision: str | None = "0001_initial_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    # 1. Rename 'tenants' table to 'organizations'
    op.rename_table("tenants", "organizations")

    # 2. Rename column 'tenant_id' to 'organization_id' in restaurants
    with op.batch_alter_table("restaurants") as batch_op:
        batch_op.alter_column("tenant_id", new_column_name="organization_id")

    # 3. Update constraints and indexes on organizations and restaurants
    with op.batch_alter_table("organizations") as batch_op:
        batch_op.drop_constraint("uq_tenants_slug", type_="unique")
        batch_op.create_unique_constraint("uq_organizations_slug", ["slug"])

    with op.batch_alter_table("restaurants") as batch_op:
        batch_op.drop_constraint("uq_restaurants_tenant_id_slug", type_="unique")
        batch_op.create_unique_constraint(
            "uq_restaurants_organization_id_slug", ["organization_id", "slug"]
        )
        batch_op.create_unique_constraint("uq_restaurants_org_id", ["organization_id", "id"])

    # 4. Create 'organization_memberships' table
    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "owner",
                "admin",
                "manager",
                "staff",
                "viewer",
                name="organization_role",
                native_enum=False,
            ),
            nullable=False,
            server_default="staff",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "invited",
                "active",
                "suspended",
                "revoked",
                name="membership_status",
                native_enum=False,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_organization_memberships_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization_memberships")),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_organization_membership_user"),
    )
    op.create_index("ix_organization_memberships_user_id", "organization_memberships", ["user_id"])
    op.create_index(
        "ix_organization_memberships_org_id",
        "organization_memberships",
        ["organization_id"],
    )

    # 5. Create 'restaurant_memberships' table
    op.create_table(
        "restaurant_memberships",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.Enum("manager", "staff", "viewer", name="restaurant_role", native_enum=False),
            nullable=False,
            server_default="staff",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_membership_org_restaurant",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_restaurant_memberships")),
        sa.UniqueConstraint("restaurant_id", "user_id", name="uq_restaurant_membership_user"),
    )
    op.create_index("ix_restaurant_memberships_user_id", "restaurant_memberships", ["user_id"])
    op.create_index(
        "ix_restaurant_memberships_org_id",
        "restaurant_memberships",
        ["organization_id"],
    )

    # 6. Create 'organization_audit_events' table
    json_type = postgresql.JSONB if is_pg else sa.JSON
    op.create_table(
        "organization_audit_events",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=64), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("metadata", json_type, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_organization_audit_events_organization_id_organizations"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organization_audit_events")),
    )
    op.create_index(
        "ix_organization_audit_events_org_created",
        "organization_audit_events",
        ["organization_id", "created_at"],
    )

    # 7. PostgreSQL Row-Level Security (RLS) policies
    if is_pg:
        op.execute("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE organizations FORCE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY organizations_tenant_isolation ON organizations
            USING (
                id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
            )
            WITH CHECK (
                id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
            );
            """
        )

        op.execute("ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE restaurants FORCE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY restaurants_tenant_isolation ON restaurants
            USING (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            )
            WITH CHECK (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            );
            """
        )

        op.execute("ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE organization_memberships FORCE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY org_memberships_tenant_isolation ON organization_memberships
            USING (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            )
            WITH CHECK (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            );
            """
        )

        op.execute("ALTER TABLE restaurant_memberships ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE restaurant_memberships FORCE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY rest_memberships_tenant_isolation ON restaurant_memberships
            USING (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            )
            WITH CHECK (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            );
            """
        )

        op.execute("ALTER TABLE organization_audit_events ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE organization_audit_events FORCE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY audit_events_tenant_isolation ON organization_audit_events
            USING (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            )
            WITH CHECK (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            );
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    if is_pg:
        op.execute(
            "DROP POLICY IF EXISTS audit_events_tenant_isolation ON organization_audit_events;"
        )
        op.execute(
            "DROP POLICY IF EXISTS rest_memberships_tenant_isolation ON restaurant_memberships;"
        )
        op.execute(
            "DROP POLICY IF EXISTS org_memberships_tenant_isolation ON organization_memberships;"
        )
        op.execute("DROP POLICY IF EXISTS restaurants_tenant_isolation ON restaurants;")
        op.execute("DROP POLICY IF EXISTS organizations_tenant_isolation ON organizations;")

    op.drop_table("organization_audit_events")
    op.drop_table("restaurant_memberships")
    op.drop_table("organization_memberships")

    with op.batch_alter_table("restaurants") as batch_op:
        batch_op.drop_constraint("uq_restaurants_org_id", type_="unique")
        batch_op.drop_constraint("uq_restaurants_organization_id_slug", type_="unique")
        batch_op.create_unique_constraint(
            "uq_restaurants_tenant_id_slug", ["organization_id", "slug"]
        )
        batch_op.alter_column("organization_id", new_column_name="tenant_id")

    with op.batch_alter_table("organizations") as batch_op:
        batch_op.drop_constraint("uq_organizations_slug", type_="unique")
        batch_op.create_unique_constraint("uq_tenants_slug", ["slug"])

    op.rename_table("organizations", "tenants")
