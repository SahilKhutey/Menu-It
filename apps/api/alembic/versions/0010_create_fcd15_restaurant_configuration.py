"""Create FCD-15 restaurant profile extensions and configuration tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_fcd15_config"
down_revision: str | None = "0009_fcd14_org_branch"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TENANT_TABLES = (
    "restaurant_branding",
    "restaurant_weekly_hours",
    "restaurant_schedule_exceptions",
    "restaurant_service_configurations",
    "restaurant_operational_settings",
    "branch_configurations",
    "branch_weekly_hours",
    "branch_service_configurations",
    "restaurant_publications",
    "restaurant_configuration_revisions",
)


def upgrade() -> None:
    json_type = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    uuid_type = sa.Uuid(as_uuid=True)

    # Extend restaurant_profiles
    op.add_column(
        "restaurant_profiles", sa.Column("short_description", sa.String(300), nullable=True)
    )
    op.add_column("restaurant_profiles", sa.Column("cuisine_type", sa.String(100), nullable=True))
    op.add_column("restaurant_profiles", sa.Column("price_range", sa.String(20), nullable=True))
    op.add_column("restaurant_profiles", sa.Column("public_email", sa.String(320), nullable=True))
    op.add_column("restaurant_profiles", sa.Column("public_phone", sa.String(30), nullable=True))
    op.add_column(
        "restaurant_profiles",
        sa.Column("social_links", json_type, nullable=False, server_default="{}"),
    )

    op.create_table(
        "restaurant_branding",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("logo_asset_id", uuid_type, nullable=True),
        sa.Column("alternate_logo_asset_id", uuid_type, nullable=True),
        sa.Column("cover_asset_id", uuid_type, nullable=True),
        sa.Column("favicon_asset_id", uuid_type, nullable=True),
        sa.Column("primary_color", sa.String(7), nullable=True),
        sa.Column("secondary_color", sa.String(7), nullable=True),
        sa.Column("accent_color", sa.String(7), nullable=True),
        sa.Column("background_color", sa.String(7), nullable=True),
        sa.Column("text_color", sa.String(7), nullable=True),
        sa.Column("font_family", sa.String(100), nullable=True),
        sa.Column("border_radius", sa.String(20), nullable=True),
        sa.Column("theme_preset", sa.String(60), nullable=True),
        sa.Column("theme_settings", json_type, nullable=False, server_default="{}"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "restaurant_id", name="uq_restaurant_branding"),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_branding_restaurant",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_restaurant_branding_org_id", "restaurant_branding", ["organization_id"])

    op.create_table(
        "restaurant_weekly_hours",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("opens_at", sa.Time(), nullable=True),
        sa.Column("closes_at", sa.Time(), nullable=True),
        sa.Column("closes_next_day", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_restaurant_weekly_weekday"),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_weekly_hours_restaurant",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_restaurant_weekly_hours_rest_day",
        "restaurant_weekly_hours",
        ["restaurant_id", "day_of_week"],
    )

    op.create_table(
        "restaurant_schedule_exceptions",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("exception_date", sa.Date(), nullable=False),
        sa.Column("exception_type", sa.String(30), nullable=False),
        sa.Column("reason", sa.String(250), nullable=True),
        sa.Column("intervals_payload", json_type, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "exception_date",
            name="uq_restaurant_schedule_exception_date",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_schedule_exception_restaurant",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "restaurant_service_configurations",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("service_type", sa.String(40), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("configuration", json_type, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "service_type",
            name="uq_restaurant_service",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_service_restaurant",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "restaurant_operational_settings",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("preparation_buffer_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("minimum_notice_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("maximum_advance_days", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("max_concurrent_orders", sa.Integer(), nullable=True),
        sa.Column("auto_accept_orders", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "holiday_behavior", sa.String(40), nullable=False, server_default="follow_exceptions"
        ),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "organization_id",
            "restaurant_id",
            name="uq_restaurant_operational_settings",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_operational_restaurant",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "branch_configurations",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("branch_id", uuid_type, nullable=False),
        sa.Column("display_name_override", sa.String(200), nullable=True),
        sa.Column("public_phone_override", sa.String(30), nullable=True),
        sa.Column(
            "schedule_override_enabled", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "service_override_enabled", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("settings", json_type, nullable=False, server_default="{}"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "branch_id", name="uq_branch_configuration"),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_configuration_parent",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "branch_weekly_hours",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("branch_id", uuid_type, nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("opens_at", sa.Time(), nullable=True),
        sa.Column("closes_at", sa.Time(), nullable=True),
        sa.Column("closes_next_day", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_branch_weekly_weekday"),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_weekly_hours_branch",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "branch_service_configurations",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("branch_id", uuid_type, nullable=False),
        sa.Column("service_type", sa.String(40), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("configuration", json_type, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "organization_id",
            "branch_id",
            "service_type",
            name="uq_branch_service",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id", "branch_id"],
            ["branches.organization_id", "branches.restaurant_id", "branches.id"],
            name="fk_branch_service_branch",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "restaurant_publications",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("public_slug", sa.String(120), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("published_revision", sa.Integer(), nullable=True),
        sa.Column("published_snapshot", json_type, nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_by", uuid_type, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "restaurant_id", name="uq_restaurant_publication"),
        sa.UniqueConstraint("public_slug", name="uq_restaurant_publication_slug"),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_publication_restaurant",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "restaurant_configuration_revisions",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("organization_id", uuid_type, nullable=False),
        sa.Column("restaurant_id", uuid_type, nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("snapshot", json_type, nullable=False),
        sa.Column("created_by", uuid_type, nullable=True),
        sa.Column("change_summary", sa.String(250), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "organization_id",
            "restaurant_id",
            "revision_number",
            name="uq_restaurant_config_revision",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "restaurant_id"],
            ["restaurants.organization_id", "restaurants.id"],
            name="fk_config_revision_restaurant",
            ondelete="CASCADE",
        ),
    )

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in _TENANT_TABLES:
            op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
            op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
            expr = "NULLIF(current_setting('app.current_organization_id', true), '')::uuid"
            op.execute(
                f"CREATE POLICY {table}_tenant_isolation ON {table} "
                f"USING (organization_id = {expr}) "
                f"WITH CHECK (organization_id = {expr})"
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in _TENANT_TABLES:
            op.execute(f"DROP POLICY IF EXISTS {table}_tenant_isolation ON {table}")

    for table in reversed(_TENANT_TABLES):
        op.drop_table(table)

    for col in (
        "social_links",
        "public_phone",
        "public_email",
        "price_range",
        "cuisine_type",
        "short_description",
    ):
        op.drop_column("restaurant_profiles", col)
