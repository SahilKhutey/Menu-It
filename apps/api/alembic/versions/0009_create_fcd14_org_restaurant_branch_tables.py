"""create FCD-14 organization, restaurant, branch, assignment, invitation, and settings tables

Revision ID: 0009_fcd14_org_branch
Revises: 0008_security_audit_events
Create Date: 2026-11-26 20:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_fcd14_org_branch"
down_revision: str | None = "0008_security_audit_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    # 1. Extend organizations table
    with op.batch_alter_table("organizations") as batch_op:
        batch_op.alter_column(
            "name", type_=sa.String(length=200), existing_type=sa.String(length=160)
        )
        batch_op.add_column(sa.Column("legal_name", sa.String(length=250), nullable=True))
        batch_op.add_column(
            sa.Column(
                "organization_type", sa.String(length=50), server_default="company", nullable=False
            )
        )
        batch_op.add_column(sa.Column("email", sa.String(length=320), nullable=True))
        batch_op.add_column(sa.Column("phone", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("website", sa.String(length=500), nullable=True))
        batch_op.add_column(
            sa.Column("country_code", sa.String(length=2), server_default="IN", nullable=False)
        )
        batch_op.add_column(
            sa.Column("currency_code", sa.String(length=3), server_default="INR", nullable=False)
        )
        batch_op.add_column(
            sa.Column("timezone", sa.String(length=100), server_default="UTC", nullable=False)
        )
        batch_op.add_column(sa.Column("created_by", sa.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column("updated_by", sa.UUID(as_uuid=True), nullable=True))

    # 2. Extend restaurants table
    with op.batch_alter_table("restaurants") as batch_op:
        batch_op.alter_column(
            "name", type_=sa.String(length=200), existing_type=sa.String(length=160)
        )
        batch_op.alter_column(
            "timezone", type_=sa.String(length=100), existing_type=sa.String(length=64)
        )
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("email", sa.String(length=320), nullable=True))
        batch_op.add_column(sa.Column("phone", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("website", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("cuisine_type", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("created_by", sa.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column("updated_by", sa.UUID(as_uuid=True), nullable=True))

    # 3. Extend organization_memberships table
    with op.batch_alter_table("organization_memberships") as batch_op:
        batch_op.add_column(sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("created_by", sa.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column("updated_by", sa.UUID(as_uuid=True), nullable=True))
    op.create_index(
        "ix_organization_memberships_user_status",
        "organization_memberships",
        ["user_id", "status"],
    )

    # 4. Create branches table
    op.create_table(
        "branches",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("branch_code", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("address_line_1", sa.String(length=250), nullable=True),
        sa.Column("address_line_2", sa.String(length=250), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state_region", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=30), nullable=True),
        sa.Column("country_code", sa.String(length=2), server_default="IN", nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("timezone", sa.String(length=100), server_default="UTC", nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "inactive",
                "suspended",
                "archived",
                name="branch_status",
                native_enum=False,
            ),
            server_default="active",
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", sa.UUID(as_uuid=True), nullable=True),
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
            name="fk_branch_restaurant_tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_branches_created_by", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["users.id"], name="fk_branches_updated_by", ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_branches"),
        sa.UniqueConstraint(
            "organization_id", "restaurant_id", "id", name="uq_branch_org_restaurant_id"
        ),
        sa.UniqueConstraint("restaurant_id", "slug", name="uq_branches_restaurant_slug"),
    )
    op.create_index("ix_branches_org_id", "branches", ["organization_id"])
    op.create_index("ix_branches_restaurant_id", "branches", ["restaurant_id"])

    # 5. Create branch_assignments table
    op.create_table(
        "branch_assignments",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("branch_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.Enum("branch_manager", "branch_staff", name="branch_role", native_enum=False),
            server_default="branch_staff",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "invited",
                "active",
                "suspended",
                "revoked",
                name="branch_assignment_status",
                native_enum=False,
            ),
            server_default="active",
            nullable=False,
        ),
        sa.Column("created_by", sa.UUID(as_uuid=True), nullable=True),
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
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_assignment_tenant_branch",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_branch_assignments_user_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name="fk_branch_assignments_created_by",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_branch_assignments"),
        sa.UniqueConstraint("branch_id", "user_id", name="uq_branch_assignment_branch_user"),
    )
    op.create_index("ix_branch_assignments_org_id", "branch_assignments", ["organization_id"])
    op.create_index("ix_branch_assignments_branch_id", "branch_assignments", ["branch_id"])
    op.create_index("ix_branch_assignments_user_id", "branch_assignments", ["user_id"])

    # 6. Create organization_invitations table
    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "owner",
                "admin",
                "manager",
                "staff",
                "viewer",
                name="invitation_role",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "accepted",
                "revoked",
                "expired",
                name="invitation_status",
                native_enum=False,
            ),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("invited_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("accepted_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
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
            name="fk_org_invitations_org_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["invited_by"], ["users.id"], name="fk_org_invitations_invited_by", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["accepted_by"],
            ["users.id"],
            name="fk_org_invitations_accepted_by",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_organization_invitations"),
        sa.UniqueConstraint("token_hash", name="uq_organization_invitations_token_hash"),
    )
    op.create_index("ix_org_invitations_org_id", "organization_invitations", ["organization_id"])
    op.create_index("ix_org_invitations_email", "organization_invitations", ["email"])
    op.create_index(
        "ix_org_invitations_token_hash", "organization_invitations", ["token_hash"], unique=True
    )

    # 7. Create organization_settings and restaurant_settings tables
    json_type = sa.JSON().with_variant(postgresql.JSONB, "postgresql")
    op.create_table(
        "organization_settings",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("settings_payload", json_type, nullable=False),
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
            name="fk_organization_settings_org_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_organization_settings"),
        sa.UniqueConstraint("organization_id", name="uq_organization_settings_organization_id"),
    )
    op.create_index(
        "ix_organization_settings_organization_id",
        "organization_settings",
        ["organization_id"],
        unique=True,
    )

    op.create_table(
        "restaurant_settings",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("settings_payload", json_type, nullable=False),
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
            name="fk_restaurant_settings_org_restaurant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_restaurant_settings"),
        sa.UniqueConstraint("restaurant_id", name="uq_restaurant_settings_restaurant_id"),
    )
    op.create_index(
        "ix_restaurant_settings_organization_id", "restaurant_settings", ["organization_id"]
    )
    op.create_index(
        "ix_restaurant_settings_restaurant_id", "restaurant_settings", ["restaurant_id"]
    )

    # 8. Enable PostgreSQL Row-Level Security (RLS) on all new tenant-scoped tables
    if is_pg:
        for tbl in [
            "branches",
            "branch_assignments",
            "organization_invitations",
            "organization_settings",
            "restaurant_settings",
        ]:
            op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
            op.execute(
                f"""
                CREATE POLICY tenant_isolation_{tbl} ON {tbl}
                FOR ALL
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
    is_pg = op.get_bind().dialect.name == "postgresql"
    if is_pg:
        for tbl in [
            "restaurant_settings",
            "organization_settings",
            "organization_invitations",
            "branch_assignments",
            "branches",
        ]:
            op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{tbl} ON {tbl};")
            op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;")

    op.drop_table("restaurant_settings")
    op.drop_table("organization_settings")
    op.drop_table("organization_invitations")
    op.drop_table("branch_assignments")
    op.drop_table("branches")

    op.drop_index("ix_organization_memberships_user_status", table_name="organization_memberships")
    with op.batch_alter_table("organization_memberships") as batch_op:
        batch_op.drop_column("updated_by")
        batch_op.drop_column("created_by")
        batch_op.drop_column("joined_at")

    with op.batch_alter_table("restaurants") as batch_op:
        batch_op.drop_column("updated_by")
        batch_op.drop_column("created_by")
        batch_op.drop_column("cuisine_type")
        batch_op.drop_column("website")
        batch_op.drop_column("phone")
        batch_op.drop_column("email")
        batch_op.drop_column("description")

    with op.batch_alter_table("organizations") as batch_op:
        batch_op.drop_column("updated_by")
        batch_op.drop_column("created_by")
        batch_op.drop_column("timezone")
        batch_op.drop_column("currency_code")
        batch_op.drop_column("country_code")
        batch_op.drop_column("website")
        batch_op.drop_column("phone")
        batch_op.drop_column("email")
        batch_op.drop_column("organization_type")
        batch_op.drop_column("legal_name")
