"""create jobs, events outbox, processed events and schedules tables (FCD-10)

Revision ID: 0007_jobs_events_schedules
Revises: 0006_files_and_notifications
Create Date: 2026-11-25 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0007_jobs_events_schedules"
down_revision: str | None = "0006_files_and_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    # 1. background_jobs table
    op.create_table(
        "background_jobs",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=150), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_user_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="queued"),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_tries", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("last_error", sa.Text(), nullable=True),
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
            name="fk_background_jobs_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_background_jobs_actor_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_background_jobs"),
        sa.UniqueConstraint("idempotency_key", name="uq_background_jobs_idempotency_key"),
    )
    op.create_index("ix_background_jobs_organization_id", "background_jobs", ["organization_id"])
    op.create_index("ix_background_jobs_status", "background_jobs", ["status"])
    op.create_index("ix_background_jobs_job_type", "background_jobs", ["job_type"])

    # 2. dead_letter_jobs table
    op.create_table(
        "dead_letter_jobs",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("job_type", sa.String(length=150), nullable=False),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
        ),
        sa.Column("failure_code", sa.String(length=100), nullable=False),
        sa.Column("failure_message", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("first_failed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dead_lettered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(length=150), nullable=False),
        sa.Column("replayed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replayed_by", sa.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_dead_letter_jobs_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["replayed_by"],
            ["users.id"],
            name="fk_dead_letter_jobs_replayed_by",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_dead_letter_jobs"),
    )
    op.create_index("ix_dead_letter_jobs_organization_id", "dead_letter_jobs", ["organization_id"])
    op.create_index("ix_dead_letter_jobs_job_id", "dead_letter_jobs", ["job_id"])
    op.create_index("ix_dead_letter_jobs_job_type", "dead_letter_jobs", ["job_type"])
    op.create_index("ix_dead_letter_jobs_dead_lettered_at", "dead_letter_jobs", ["dead_lettered_at"])

    # 3. event_outbox table
    op.create_table(
        "event_outbox",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=150), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_user_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("correlation_id", sa.String(length=150), nullable=False),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=100), nullable=True),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(length=150), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_event_outbox_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name="fk_event_outbox_actor_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_event_outbox"),
        sa.UniqueConstraint("event_id", name="uq_event_outbox_event_id"),
    )
    op.create_index("ix_event_outbox_organization_id", "event_outbox", ["organization_id"])
    op.create_index("ix_event_outbox_event_type", "event_outbox", ["event_type"])
    op.create_index("ix_event_outbox_published_at", "event_outbox", ["published_at"])
    op.create_index("ix_event_outbox_next_attempt_at", "event_outbox", ["next_attempt_at"])
    op.create_index("ix_event_outbox_occurred_at", "event_outbox", ["occurred_at"])

    # 4. processed_events table (consumer inbox)
    op.create_table(
        "processed_events",
        sa.Column("consumer_name", sa.String(length=150), nullable=False),
        sa.Column("event_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("consumer_name", "event_id", name="pk_processed_events"),
    )

    # 5. scheduled_jobs table
    op.create_table(
        "scheduled_jobs",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("job_type", sa.String(length=150), nullable=False),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
        ),
        sa.Column("schedule_type", sa.String(length=30), nullable=False),
        sa.Column("schedule_expression", sa.String(length=150), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=False, server_default="UTC"),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
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
            name="fk_scheduled_jobs_organization_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_scheduled_jobs"),
    )
    op.create_index("ix_scheduled_jobs_organization_id", "scheduled_jobs", ["organization_id"])
    op.create_index("ix_scheduled_jobs_job_type", "scheduled_jobs", ["job_type"])
    op.create_index("ix_scheduled_jobs_next_run_at", "scheduled_jobs", ["next_run_at"])
    op.create_index("ix_scheduled_jobs_enabled", "scheduled_jobs", ["enabled"])

    # 6. scheduled_job_runs table
    op.create_table(
        "scheduled_job_runs",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("scheduled_job_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("run_key", sa.String(length=255), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="completed"),
        sa.Column("job_id", sa.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["scheduled_job_id"],
            ["scheduled_jobs.id"],
            name="fk_scheduled_job_runs_job_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_scheduled_job_runs"),
        sa.UniqueConstraint("run_key", name="uq_scheduled_job_runs_run_key"),
    )
    op.create_index("ix_scheduled_job_runs_job_id", "scheduled_job_runs", ["scheduled_job_id"])

    # Row-Level Security Policies for PostgreSQL
    if is_pg:
        for tbl in ["background_jobs", "dead_letter_jobs", "event_outbox", "scheduled_jobs"]:
            op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            op.execute(
                f"""
                CREATE POLICY tenant_isolation_{tbl} ON {tbl}
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
        for tbl in ["scheduled_jobs", "event_outbox", "dead_letter_jobs", "background_jobs"]:
            op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{tbl} ON {tbl};")

    op.drop_table("scheduled_job_runs")
    op.drop_table("scheduled_jobs")
    op.drop_table("processed_events")
    op.drop_table("event_outbox")
    op.drop_table("dead_letter_jobs")
    op.drop_table("background_jobs")
