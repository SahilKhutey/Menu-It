"""create idempotency records table (FCD-07 WP-11)

Revision ID: 0005_idempotency_records
Revises: 0004_restaurant_profiles
Create Date: 2026-11-24 11:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0005_idempotency_records"
down_revision: str | None = "0004_restaurant_profiles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    op.create_table(
        "idempotency_records",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=False),
        sa.Column(
            "response_body",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_idempotency_records_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            name="fk_idempotency_records_actor_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_idempotency_records"),
        sa.UniqueConstraint(
            "organization_id",
            "actor_id",
            "key",
            name="uq_idempotency_org_actor_key",
        ),
    )

    op.create_index(
        "ix_idempotency_records_org_id",
        "idempotency_records",
        ["organization_id"],
    )
    op.create_index(
        "ix_idempotency_records_actor_id",
        "idempotency_records",
        ["actor_id"],
    )
    op.create_index(
        "ix_idempotency_records_key",
        "idempotency_records",
        ["key"],
    )
    op.create_index(
        "ix_idempotency_records_org_key",
        "idempotency_records",
        ["organization_id", "key"],
    )
    op.create_index(
        "ix_idempotency_records_expires_at",
        "idempotency_records",
        ["expires_at"],
    )

    # Enable RLS if PostgreSQL
    if is_pg:
        op.execute("ALTER TABLE idempotency_records ENABLE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY tenant_isolation_idempotency_records ON idempotency_records
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
        op.execute(
            "DROP POLICY IF EXISTS tenant_isolation_idempotency_records ON idempotency_records;"
        )

    op.drop_index("ix_idempotency_records_expires_at", table_name="idempotency_records")
    op.drop_index("ix_idempotency_records_org_key", table_name="idempotency_records")
    op.drop_index("ix_idempotency_records_key", table_name="idempotency_records")
    op.drop_index("ix_idempotency_records_actor_id", table_name="idempotency_records")
    op.drop_index("ix_idempotency_records_org_id", table_name="idempotency_records")
    op.drop_table("idempotency_records")
