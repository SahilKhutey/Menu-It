"""create security audit events table with PostgreSQL RLS (FCD-11 WP-07)

Revision ID: 0008_security_audit_events
Revises: 0007_jobs_events_schedules
Create Date: 2026-11-26 09:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0008_security_audit_events"
down_revision: str | None = "0007_jobs_events_schedules"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    op.create_table(
        "security_audit_events",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("outcome", sa.String(length=50), nullable=False),
        sa.Column("actor_user_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "actor_type",
            sa.String(length=50),
            server_default="user",
            nullable=False,
        ),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("restaurant_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("correlation_id", sa.String(length=255), nullable=True),
        sa.Column("source_ip", sa.String(length=100), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("reason_code", sa.String(length=100), nullable=True),
        sa.Column(
            "metadata",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_security_audit_events_actor_user_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_security_audit_events_organization_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurants.id"],
            name="fk_security_audit_events_restaurant_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_security_audit_events"),
        sa.UniqueConstraint("event_id", name="uq_security_audit_events_event_id"),
    )

    op.create_index(
        "ix_security_audit_events_occurred_at",
        "security_audit_events",
        ["occurred_at"],
    )
    op.create_index(
        "ix_security_audit_events_org_occurred",
        "security_audit_events",
        ["organization_id", "occurred_at"],
    )
    op.create_index(
        "ix_security_audit_events_actor_user",
        "security_audit_events",
        ["actor_user_id"],
    )
    op.create_index(
        "ix_security_audit_events_event_type",
        "security_audit_events",
        ["event_type"],
    )
    op.create_index(
        "ix_security_audit_events_outcome",
        "security_audit_events",
        ["outcome"],
    )
    op.create_index(
        "ix_security_audit_events_correlation",
        "security_audit_events",
        ["correlation_id"],
    )

    if is_pg:
        op.execute("ALTER TABLE security_audit_events ENABLE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY tenant_isolation_security_audit_events ON security_audit_events
            FOR ALL
            USING (
                organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
                OR organization_id IS NULL
            );
            """
        )


def downgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    if is_pg:
        op.execute(
            "DROP POLICY IF EXISTS tenant_isolation_security_audit_events ON security_audit_events;"
        )
        op.execute("ALTER TABLE security_audit_events DISABLE ROW LEVEL SECURITY;")

    op.drop_table("security_audit_events")
