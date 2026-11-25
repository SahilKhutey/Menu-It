"""create files and notifications tables (FCD-09 WP-02, WP-03)

Revision ID: 0006_files_and_notifications
Revises: 0005_idempotency_records
Create Date: 2026-11-25 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0006_files_and_notifications"
down_revision: str | None = "0005_idempotency_records"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    # 1. files table
    op.create_table(
        "files",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("uploaded_by", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("original_filename", sa.String(length=180), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("visibility", sa.String(length=32), nullable=False, server_default="tenant_private"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="stored"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_files_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name="fk_files_uploaded_by",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_files"),
        sa.UniqueConstraint("storage_key", name="uq_files_storage_key"),
    )

    op.create_index("ix_files_organization_id", "files", ["organization_id"])
    op.create_index("ix_files_uploaded_by", "files", ["uploaded_by"])
    op.create_index("ix_files_status", "files", ["status"])
    op.create_index("ix_files_visibility", "files", ["visibility"])
    op.create_index("ix_files_created_at", "files", ["created_at"])

    # 2. notifications table
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("recipient_user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("body", sa.String(length=1024), nullable=False),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=True,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_notifications_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recipient_user_id"],
            ["users.id"],
            name="fk_notifications_recipient_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_notifications"),
    )

    op.create_index("ix_notifications_org_id", "notifications", ["organization_id"])
    op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_user_id"])
    op.create_index("ix_notifications_recipient_read", "notifications", ["recipient_user_id", "read_at"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])

    # 3. notification_deliveries table
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("notification_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("provider_reference", sa.String(length=256), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
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
            ["notification_id"],
            ["notifications.id"],
            name="fk_notification_deliveries_notification_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_notification_deliveries"),
        sa.UniqueConstraint("idempotency_key", name="uq_notification_deliveries_idempotency_key"),
    )

    op.create_index("ix_notification_deliveries_notification_id", "notification_deliveries", ["notification_id"])
    op.create_index("ix_notification_deliveries_channel_status", "notification_deliveries", ["channel", "status"])

    # 4. Enable Row Level Security (RLS) on PostgreSQL
    if is_pg:
        op.execute("ALTER TABLE files ENABLE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY tenant_isolation_files ON files
            FOR ALL
            USING (
                visibility = 'public'
                OR (
                    organization_id IS NOT NULL
                    AND organization_id = NULLIF(
                        current_setting('app.current_organization_id', true), ''
                    )::uuid
                )
            )
            WITH CHECK (
                organization_id IS NOT NULL
                AND organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            );
            """
        )

        op.execute("ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;")
        op.execute(
            """
            CREATE POLICY tenant_isolation_notifications ON notifications
            FOR ALL
            USING (
                organization_id IS NULL
                OR organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            )
            WITH CHECK (
                organization_id IS NULL
                OR organization_id = NULLIF(
                    current_setting('app.current_organization_id', true), ''
                )::uuid
            );
            """
        )


def downgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    if is_pg:
        op.execute("DROP POLICY IF EXISTS tenant_isolation_notifications ON notifications;")
        op.execute("DROP POLICY IF EXISTS tenant_isolation_files ON files;")

    op.drop_table("notification_deliveries")
    op.drop_table("notifications")
    op.drop_table("files")
