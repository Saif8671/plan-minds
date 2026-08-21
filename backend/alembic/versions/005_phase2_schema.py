"""Phase 2 schema: conversations, preferences, push_subscriptions, habit_profiles, etc.

Revision ID: 005_phase2_schema
Revises: 004
Create Date: 2026-08-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "005_phase2_schema"
down_revision = "004"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # ── 1. Create Enums ─────────────────────────────────────────────
    routinecategory = sa.Enum('work', 'study', 'health', 'personal', 'social', 'other', name='routinecategory')
    routinecategory.create(op.get_bind(), checkfirst=True)

    taskpriority = sa.Enum('low', 'medium', 'high', 'urgent', name='taskpriority')
    taskpriority.create(op.get_bind(), checkfirst=True)

    recurrencetype = sa.Enum('daily', 'weekly', 'monthly', 'custom', name='recurrencetype')
    recurrencetype.create(op.get_bind(), checkfirst=True)

    conversationstatus = sa.Enum('active', 'archived', name='conversationstatus')
    conversationstatus.create(op.get_bind(), checkfirst=True)

    schedulingstyle = sa.Enum('strict', 'flexible', name='schedulingstyle')
    schedulingstyle.create(op.get_bind(), checkfirst=True)

    reminderoutcome = sa.Enum('sent', 'snoozed', 'dismissed', 'missed', name='reminderoutcome')
    reminderoutcome.create(op.get_bind(), checkfirst=True)

    # ── 2. push_subscriptions ───────────────────────────────────────
    op.create_table('push_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('endpoint', sa.String(length=512), nullable=False),
        sa.Column('p256dh', sa.String(length=255), nullable=False),
        sa.Column('auth', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_push_subscriptions_user_id', 'push_subscriptions', ['user_id'], unique=False)

    # ── 3. user_preferences ─────────────────────────────────────────
    op.create_table('user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('wake_time', sa.Time(), nullable=True),
        sa.Column('sleep_time', sa.Time(), nullable=True),
        sa.Column('work_start', sa.Time(), nullable=True),
        sa.Column('work_end', sa.Time(), nullable=True),
        sa.Column('college_start', sa.Time(), nullable=True),
        sa.Column('college_end', sa.Time(), nullable=True),
        sa.Column('break_duration_minutes', sa.Integer(), nullable=False, server_default="15"),
        sa.Column('preferred_study_time', sa.String(length=32), nullable=True),
        sa.Column('preferred_workout_time', sa.String(length=32), nullable=True),
        sa.Column('notification_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timezone', sa.String(length=64), nullable=False, server_default="UTC"),
        sa.Column('working_days', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('meals', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('scheduling_style', postgresql.ENUM('strict', 'flexible', name='schedulingstyle', create_type=False), nullable=True),
        sa.Column('default_buffer_time_minutes', sa.Integer(), nullable=False, server_default="15"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)

    # ── 4. conversations ─────────────────────────────────────────────
    op.create_table('conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'archived', name='conversationstatus', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'], unique=False)
    
    op.create_table('conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversation_messages_conversation_id', 'conversation_messages', ['conversation_id'], unique=False)
    
    op.create_table('conversation_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_state', sa.String(length=64), nullable=False),
        sa.Column('missing_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversation_states_conversation_id', 'conversation_states', ['conversation_id'], unique=True)

    # ── 5. habit_profiles ─────────────────────────────────────────────
    op.create_table('habit_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completion_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('preferred_study_hour', sa.Integer(), nullable=True),
        sa.Column('preferred_workout_hour', sa.Integer(), nullable=True),
        sa.Column('avg_delay_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('focus_session_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('total_completions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_habit_profiles_user_id', 'habit_profiles', ['user_id'])

    # ── 6. reminder_history ───────────────────────────────────────────
    op.create_table('reminder_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reminder_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fired_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('outcome', postgresql.ENUM('sent', 'snoozed', 'dismissed', 'missed', name='reminderoutcome', create_type=False), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['reminder_id'], ['reminders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminder_history_reminder', 'reminder_history', ['reminder_id', 'fired_at'])

    # ── 7. New columns ────────────────────────────────────────────────
    op.add_column('notifications', sa.Column('is_delivered', sa.Boolean(), nullable=False, server_default="false"))
    op.add_column('reminders', sa.Column('is_snoozed', sa.Boolean(), nullable=False, server_default="false"))
    op.add_column('reminders', sa.Column('snooze_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reminders', sa.Column('is_completed', sa.Boolean(), nullable=False, server_default="false"))
    op.add_column('routines', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('routines', sa.Column('category', postgresql.ENUM('work', 'study', 'health', 'personal', 'social', 'other', name='routinecategory', create_type=False), nullable=False, server_default="other"))
    op.add_column('routines', sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'urgent', name='taskpriority', create_type=False), nullable=False, server_default="medium"))
    op.add_column('routines', sa.Column('frequency', postgresql.ENUM('daily', 'weekly', 'monthly', 'custom', name='recurrencetype', create_type=False), nullable=True))
    op.add_column('routines', sa.Column('estimated_duration', sa.Integer(), nullable=False, server_default="60"))
    op.add_column('routines', sa.Column('preferred_time', sa.Time(), nullable=True))
    op.add_column('routines', sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('tasks', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('labels', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    op.add_column('reminders', sa.Column('recurrence', postgresql.ENUM('daily', 'weekly', 'monthly', 'custom', name='recurrencetype', create_type=False), nullable=True))
    op.add_column('reminders', sa.Column('recurrence_rule', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('reminders', sa.Column('next_fire', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_reminders_next_fire', 'reminders', ['next_fire'])
    op.create_index('ix_reminders_fire_time', 'reminders', ['reminder_time'])
    op.create_index('ix_reminders_user_sent', 'reminders', ['user_id', 'is_sent'])

    op.add_column('activity_logs', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('activity_logs', sa.Column('delay_minutes', sa.Integer(), nullable=True))
    op.add_column('activity_logs', sa.Column('skipped_reason', sa.String(512), nullable=True))
    
    op.create_foreign_key('fk_activity_logs_user_id', 'activity_logs', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    
    op.create_index('ix_activity_logs_task_created', 'activity_logs', ['task_id', 'created_at'])
    op.create_index('ix_activity_logs_user', 'activity_logs', ['user_id'])
    
    op.create_index('ix_tasks_user_status', 'tasks', ['user_id', 'status'])
    op.create_index('ix_schedules_user_date', 'schedules', ['user_id', 'date'])
    op.create_index('ix_notifications_user_read', 'notifications', ['user_id', 'is_read'])

def downgrade() -> None:
    # Drop Indexes
    op.drop_index('ix_notifications_user_read', table_name='notifications')
    op.drop_index('ix_schedules_user_date', table_name='schedules')
    op.drop_index('ix_tasks_user_status', table_name='tasks')
    op.drop_index('ix_activity_logs_user', table_name='activity_logs')
    op.drop_index('ix_activity_logs_task_created', table_name='activity_logs')
    op.drop_index('ix_reminders_user_sent', table_name='reminders')
    op.drop_index('ix_reminders_fire_time', table_name='reminders')
    op.drop_index('ix_reminders_next_fire', table_name='reminders')

    # Drop Foreign Keys
    op.drop_constraint('fk_activity_logs_user_id', 'activity_logs', type_='foreignkey')

    # Drop Columns
    op.drop_column('activity_logs', 'skipped_reason')
    op.drop_column('activity_logs', 'delay_minutes')
    op.drop_column('activity_logs', 'user_id')

    op.drop_column('reminders', 'next_fire')
    op.drop_column('reminders', 'recurrence_rule')
    op.drop_column('reminders', 'recurrence')

    op.drop_column('tasks', 'labels')
    op.drop_column('tasks', 'notes')

    op.drop_column('routines', 'tags')
    op.drop_column('routines', 'preferred_time')
    op.drop_column('routines', 'estimated_duration')
    op.drop_column('routines', 'frequency')
    op.drop_column('routines', 'priority')
    op.drop_column('routines', 'category')
    op.drop_column('routines', 'description')

    op.drop_column('reminders', 'is_completed')
    op.drop_column('reminders', 'snooze_until')
    op.drop_column('reminders', 'is_snoozed')
    op.drop_column('notifications', 'is_delivered')

    # Drop Tables
    op.drop_table('reminder_history')
    op.drop_table('habit_profiles')
    op.drop_table('conversation_states')
    op.drop_table('conversation_messages')
    op.drop_table('conversations')
    op.drop_table('user_preferences')
    op.drop_table('push_subscriptions')

    # Drop Enums specific to this migration
    sa.Enum(name='reminderoutcome').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='schedulingstyle').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='conversationstatus').drop(op.get_bind(), checkfirst=True)
