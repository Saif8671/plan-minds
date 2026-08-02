"""Add notifications, routines, ai_analyses tables and update schedules/tasks

Revision ID: 002
Revises: 001
Create Date: 2026-07-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── New enum types ──────────────────────────────────────────────
    schedule_status = postgresql.ENUM(
        "draft",
        "active",
        "completed",
        "cancelled",
        name="schedulestatus",
        create_type=False,
    )
    notification_type = postgresql.ENUM(
        "schedule_generated",
        "task_reminder",
        "task_completed",
        "task_missed",
        "system",
        name="notificationtype",
        create_type=False,
    )
    recurrence_type = postgresql.ENUM(
        "daily",
        "weekly",
        "monthly",
        "custom",
        name="recurrencetype",
        create_type=False,
    )

    schedule_status.create(op.get_bind(), checkfirst=True)
    notification_type.create(op.get_bind(), checkfirst=True)
    recurrence_type.create(op.get_bind(), checkfirst=True)

    # ── Update schedules table ──────────────────────────────────────
    op.add_column("schedules", sa.Column("title", sa.String(255), nullable=True))
    op.add_column("schedules", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "schedules",
        sa.Column(
            "priority",
            sa.Enum(
                "low",
                "medium",
                "high",
                "urgent",
                name="taskpriority",
                create_type=False,
            ),
            server_default="medium",
        ),
    )
    op.add_column(
        "schedules", sa.Column("start_time", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "schedules", sa.Column("end_time", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "schedules", sa.Column("status", schedule_status, server_default="active")
    )
    op.add_column(
        "schedules",
        sa.Column(
            "category",
            sa.Enum(
                "work",
                "study",
                "health",
                "personal",
                "meal",
                "sleep",
                "other",
                name="taskcategory",
                create_type=False,
            ),
            server_default="other",
        ),
    )
    op.add_column(
        "schedules",
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    # Back-fill title for existing rows so we can set NOT NULL
    op.execute("UPDATE schedules SET title = 'Untitled Schedule' WHERE title IS NULL")
    op.alter_column("schedules", "title", nullable=False)

    # Back-fill start/end times for existing rows
    op.execute("UPDATE schedules SET start_time = created_at WHERE start_time IS NULL")
    op.execute(
        "UPDATE schedules SET end_time = created_at + interval '1 day' WHERE end_time IS NULL"
    )
    op.alter_column("schedules", "start_time", nullable=False)
    op.alter_column("schedules", "end_time", nullable=False)

    # Make generated_schedule nullable (it's only set by AI generation)
    op.alter_column("schedules", "generated_schedule", nullable=True)

    # ── Update tasks table ──────────────────────────────────────────
    op.add_column(
        "tasks", sa.Column("schedule_id", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_foreign_key(
        "fk_tasks_schedule_id",
        "tasks",
        "schedules",
        ["schedule_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_tasks_schedule_id", "tasks", ["schedule_id"])
    op.add_column("tasks", sa.Column("completed", sa.Boolean(), server_default="false"))
    op.add_column(
        "tasks", sa.Column("reminder_time", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "tasks",
        sa.Column(
            "recurrence",
            sa.Enum(
                "daily",
                "weekly",
                "monthly",
                "custom",
                name="recurrencetype",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    # ── Create notifications table ──────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("notification_type", notification_type, server_default="system"),
        sa.Column("is_read", sa.Boolean(), server_default="false"),
        sa.Column("data", postgresql.JSONB()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    # ── Create routines table ───────────────────────────────────────
    op.create_table(
        "routines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("routine_text", sa.Text(), nullable=False),
        sa.Column("parsed_data", postgresql.JSONB()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    # ── Create ai_analyses table ────────────────────────────────────
    op.create_table(
        "ai_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("analysis_result", postgresql.JSONB(), nullable=False),
        sa.Column("model_used", sa.String(128)),
        sa.Column("confidence_score", sa.Float()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("ai_analyses")
    op.drop_table("routines")
    op.drop_table("notifications")

    # ── Revert tasks changes ────────────────────────────────────────
    op.drop_index("ix_tasks_schedule_id", table_name="tasks")
    op.drop_constraint("fk_tasks_schedule_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "recurrence")
    op.drop_column("tasks", "reminder_time")
    op.drop_column("tasks", "completed")
    op.drop_column("tasks", "schedule_id")

    # ── Revert schedules changes ────────────────────────────────────
    op.drop_column("schedules", "updated_at")
    op.drop_column("schedules", "category")
    op.drop_column("schedules", "status")
    op.drop_column("schedules", "end_time")
    op.drop_column("schedules", "start_time")
    op.drop_column("schedules", "priority")
    op.drop_column("schedules", "description")
    op.drop_column("schedules", "title")
    op.alter_column("schedules", "generated_schedule", nullable=False)

    # ── Drop new enums ──────────────────────────────────────────────
    op.execute("DROP TYPE IF EXISTS recurrencetype")
    op.execute("DROP TYPE IF EXISTS notificationtype")
    op.execute("DROP TYPE IF EXISTS schedulestatus")
