"""create identity and auth foundation (FCD-05 §5.2, §20)

Revision ID: 0003_identity_foundation
Revises: 0002_org_foundation
Create Date: 2026-11-24 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_identity_foundation"
down_revision: str | None = "0002_org_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create 'users' table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("normalized_email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("email_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("normalized_email", name="uq_users_normalized_email"),
    )
    op.create_index("ix_users_normalized_email", "users", ["normalized_email"])
    op.create_index("ix_users_status", "users", ["status"])

    # 2. Create 'user_credentials' table
    op.create_table(
        "user_credentials",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_user_credentials"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_credentials_user_id_users",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", name="uq_user_credentials_user_id"),
    )
    op.create_index("ix_user_credentials_user_id", "user_credentials", ["user_id"])

    # 3. Create 'user_sessions' table
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_user_sessions"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_sessions_user_id_users",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_index("ix_user_sessions_status", "user_sessions", ["status"])
    op.create_index("ix_user_sessions_expires_at", "user_sessions", ["expires_at"])

    # 4. Create 'refresh_token_records' table
    op.create_table(
        "refresh_token_records",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("family_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("is_consumed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_refresh_token_records"),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["user_sessions.id"],
            name="fk_refresh_token_records_session_id_user_sessions",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("token_hash", name="uq_refresh_token_records_token_hash"),
    )
    op.create_index("ix_refresh_token_records_session_id", "refresh_token_records", ["session_id"])
    op.create_index("ix_refresh_token_records_token_hash", "refresh_token_records", ["token_hash"])
    op.create_index("ix_refresh_token_records_family_id", "refresh_token_records", ["family_id"])
    op.create_index("ix_refresh_token_records_expires_at", "refresh_token_records", ["expires_at"])

    # 5. Create 'email_verification_tokens' table
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_email_verification_tokens"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_email_verification_tokens_user_id_users",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("token_hash", name="uq_email_verification_tokens_token_hash"),
    )
    op.create_index(
        "ix_email_verification_tokens_user_id", "email_verification_tokens", ["user_id"]
    )
    op.create_index(
        "ix_email_verification_tokens_token_hash", "email_verification_tokens", ["token_hash"]
    )

    # 6. Create 'password_reset_tokens' table
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_password_reset_tokens"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_password_reset_tokens_user_id_users",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("token_hash", name="uq_password_reset_tokens_token_hash"),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"])

    # 7. Create 'platform_memberships' table
    op.create_table(
        "platform_memberships",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
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
        sa.PrimaryKeyConstraint("id", name="pk_platform_memberships"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_platform_memberships_user_id_users",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id", name="uq_platform_memberships_user_id"),
    )
    op.create_index("ix_platform_memberships_user_id", "platform_memberships", ["user_id"])

    # 8. Reconcile existing membership references
    bind = op.get_bind()
    conn = bind.connection if hasattr(bind, "connection") else bind

    # Check for any existing orphaned user_ids in organization_memberships
    try:
        org_users = conn.execute(
            sa.text(
                "SELECT DISTINCT user_id FROM organization_memberships "
                "WHERE user_id NOT IN (SELECT id FROM users)"
            )
        ).fetchall()
        for row in org_users:
            uid = row[0]
            conn.execute(
                sa.text(
                    "INSERT INTO users (id, email, normalized_email, display_name, status, "
                    "email_verified, created_at, updated_at) VALUES "
                    "(:uid, :email, :n_email, 'Reconciled User', 'active', true, "
                    "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ),
                {
                    "uid": uid,
                    "email": f"reconciled_{uid}@placeholder.menu-it.internal",
                    "n_email": f"reconciled_{uid}@placeholder.menu-it.internal",
                },
            )
    except Exception:
        pass

    # Check for any existing orphaned user_ids in restaurant_memberships
    try:
        rest_users = conn.execute(
            sa.text(
                "SELECT DISTINCT user_id FROM restaurant_memberships "
                "WHERE user_id NOT IN (SELECT id FROM users)"
            )
        ).fetchall()
        for row in rest_users:
            uid = row[0]
            conn.execute(
                sa.text(
                    "INSERT INTO users (id, email, normalized_email, display_name, status, "
                    "email_verified, created_at, updated_at) VALUES "
                    "(:uid, :email, :n_email, 'Reconciled User', 'active', true, "
                    "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ),
                {
                    "uid": uid,
                    "email": f"reconciled_{uid}@placeholder.menu-it.internal",
                    "n_email": f"reconciled_{uid}@placeholder.menu-it.internal",
                },
            )
    except Exception:
        pass

    # Add foreign keys on organization_memberships and restaurant_memberships
    with op.batch_alter_table("organization_memberships") as batch_op:
        batch_op.create_foreign_key(
            "fk_organization_memberships_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("restaurant_memberships") as batch_op:
        batch_op.create_foreign_key(
            "fk_restaurant_memberships_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    # Drop foreign keys on membership tables
    with op.batch_alter_table("restaurant_memberships") as batch_op:
        batch_op.drop_constraint("fk_restaurant_memberships_user_id_users", type_="foreignkey")

    with op.batch_alter_table("organization_memberships") as batch_op:
        batch_op.drop_constraint("fk_organization_memberships_user_id_users", type_="foreignkey")

    # Drop tables in reverse dependency order
    op.drop_table("platform_memberships")
    op.drop_table("password_reset_tokens")
    op.drop_table("email_verification_tokens")
    op.drop_table("refresh_token_records")
    op.drop_table("user_sessions")
    op.drop_table("user_credentials")
    op.drop_table("users")
