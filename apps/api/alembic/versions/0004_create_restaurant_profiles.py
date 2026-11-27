"""create restaurant profiles table and tenant rls (FCD-06 §14.4)

Revision ID: 0004_restaurant_profiles
Revises: 0003_identity_foundation
Create Date: 2026-11-24 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0004_restaurant_profiles"
down_revision: str | None = "0003_identity_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    op.create_table(
        "restaurant_profiles",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("public_name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address_line_1", sa.String(length=255), nullable=True),
        sa.Column("address_line_2", sa.String(length=255), nullable=True),
        sa.Column("address_locality", sa.String(length=100), nullable=True),
        sa.Column("address_admin_area", sa.String(length=100), nullable=True),
        sa.Column("address_postal_code", sa.String(length=20), nullable=True),
        sa.Column("address_country_code", sa.String(length=2), nullable=True),
        sa.Column("primary_currency", sa.String(length=3), server_default="USD", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="UTC", nullable=False),
        sa.Column(
            "schedule_payload",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column("website_url", sa.String(length=2048), nullable=True),
        sa.Column("logo_asset_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("banner_asset_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_restaurant_profiles"),
        sa.UniqueConstraint("restaurant_id", name="uq_restaurant_profiles_restaurant_id"),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_restaurant_profiles_org_restaurant",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_restaurant_profiles_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurants.id"],
            name="fk_restaurant_profiles_restaurant_id",
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_restaurant_profiles_organization_id",
        "restaurant_profiles",
        ["organization_id"],
    )
    op.create_index(
        "ix_restaurant_profiles_restaurant_id",
        "restaurant_profiles",
        ["restaurant_id"],
    )

    if is_pg:
        op.execute("ALTER TABLE restaurant_profiles ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE restaurant_profiles FORCE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY restaurant_profiles_tenant_isolation ON restaurant_profiles
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
        op.execute(
            "DROP POLICY IF EXISTS restaurant_profiles_tenant_isolation ON restaurant_profiles;"
        )
        op.execute("ALTER TABLE restaurant_profiles DISABLE ROW LEVEL SECURITY;")

    op.drop_index("ix_restaurant_profiles_restaurant_id", table_name="restaurant_profiles")
    op.drop_index("ix_restaurant_profiles_organization_id", table_name="restaurant_profiles")
    op.drop_table("restaurant_profiles")
