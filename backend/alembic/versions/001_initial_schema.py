"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("age", sa.Integer()),
        sa.Column("occupation", sa.String(255)),
        sa.Column("timezone", sa.String(64), server_default="UTC"),
        sa.Column("wake_time", sa.Time()),
        sa.Column("sleep_time", sa.Time()),
        sa.Column("working_days", postgresql.JSONB()),
        sa.Column("preferred_study_hours", postgresql.JSONB()),
        sa.Column("reminder_preferences", postgresql.JSONB()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    task_priority = postgresql.ENUM(
        "low", "medium", "high", "urgent", name="taskpriority", create_type=False
    )
    task_status = postgresql.ENUM(
        "pending",
        "in_progress",
        "completed",
        "skipped",
        "cancelled",
        name="taskstatus",
        create_type=False,
    )
    task_category = postgresql.ENUM(
        "work",
        "study",
        "health",
        "personal",
        "meal",
        "sleep",
        "other",
        name="taskcategory",
        create_type=False,
    )
    reminder_type = postgresql.ENUM(
        "task",
        "meal",
        "water",
        "sleep",
        "medication",
        "custom",
        name="remindertype",
        create_type=False,
    )
    activity_status = postgresql.ENUM(
        "started", "completed", "skipped", name="activitystatus", create_type=False
    )

    task_priority.create(op.get_bind(), checkfirst=True)
    task_status.create(op.get_bind(), checkfirst=True)
    task_category.create(op.get_bind(), checkfirst=True)
    reminder_type.create(op.get_bind(), checkfirst=True)
    activity_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("priority", task_priority, server_default="medium"),
        sa.Column("category", task_category, server_default="other"),
        sa.Column("duration", sa.Integer(), server_default="60"),
        sa.Column("deadline", sa.DateTime(timezone=True)),
        sa.Column("is_fixed", sa.Boolean(), server_default="false"),
        sa.Column("fixed_start", sa.Time()),
        sa.Column("fixed_end", sa.Time()),
        sa.Column("is_recurring", sa.Boolean(), server_default="false"),
        sa.Column("recurrence_rule", postgresql.JSONB()),
        sa.Column("status", task_status, server_default="pending"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("generated_schedule", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="SET NULL"),
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("reminder_type", reminder_type, server_default="custom"),
        sa.Column("reminder_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_sent", sa.Boolean(), server_default="false"),
        sa.Column("message", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("time_spent", sa.Integer()),
        sa.Column("status", activity_status, server_default="started"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("activity_logs")
    op.drop_table("reminders")
    op.drop_table("schedules")
    op.drop_table("tasks")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS activitystatus")
    op.execute("DROP TYPE IF EXISTS remindertype")
    op.execute("DROP TYPE IF EXISTS taskcategory")
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS taskpriority")
