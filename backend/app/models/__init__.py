import enum
import uuid
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TaskCategory(str, enum.Enum):
    WORK = "work"
    STUDY = "study"
    HEALTH = "health"
    PERSONAL = "personal"
    MEAL = "meal"
    SLEEP = "sleep"
    OTHER = "other"


class ScheduleStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReminderType(str, enum.Enum):
    TASK = "task"
    MEAL = "meal"
    WATER = "water"
    SLEEP = "sleep"
    MEDICATION = "medication"
    CUSTOM = "custom"


class ReminderOutcome(str, enum.Enum):
    SENT = "sent"
    SNOOZED = "snoozed"
    DISMISSED = "dismissed"
    MISSED = "missed"


class NotificationType(str, enum.Enum):
    SCHEDULE_GENERATED = "schedule_generated"
    TASK_REMINDER = "task_reminder"
    TASK_COMPLETED = "task_completed"
    TASK_MISSED = "task_missed"
    SYSTEM = "system"


class ActivityStatus(str, enum.Enum):
    STARTED = "started"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class RecurrenceType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RoutineCategory(str, enum.Enum):
    WORK = "work"
    STUDY = "study"
    HEALTH = "health"
    PERSONAL = "personal"
    SOCIAL = "social"
    OTHER = "other"


class SchedulingStyle(str, enum.Enum):
    STRICT = "strict"
    FLEXIBLE = "flexible"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


# ─── User ──────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    firebase_uid: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )
    google_sub: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    age: Mapped[int | None] = mapped_column(Integer)
    occupation: Mapped[str | None] = mapped_column(String(255))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    wake_time: Mapped[time | None] = mapped_column(Time)
    sleep_time: Mapped[time | None] = mapped_column(Time)
    working_days: Mapped[list | None] = mapped_column(JSONB, default=list)
    preferred_study_hours: Mapped[dict | None] = mapped_column(JSONB)
    reminder_preferences: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    reset_otp: Mapped[str | None] = mapped_column(String(6))
    reset_otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    task_occurrences: Mapped[list["TaskOccurrence"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    routines: Mapped[list["Routine"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    ai_analyses: Mapped[list["AIAnalysis"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    push_subscriptions: Mapped[list["PushSubscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    stats: Mapped[Optional["UserStats"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    habit_profile: Mapped[Optional["HabitProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )


# ─── UserPreferences ──────────────────────────────────────────────────


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    wake_time: Mapped[time | None] = mapped_column(Time)
    sleep_time: Mapped[time | None] = mapped_column(Time)
    work_start: Mapped[time | None] = mapped_column(Time)
    work_end: Mapped[time | None] = mapped_column(Time)
    college_start: Mapped[time | None] = mapped_column(Time)
    college_end: Mapped[time | None] = mapped_column(Time)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=15)
    preferred_study_time: Mapped[str | None] = mapped_column(String(32))
    preferred_workout_time: Mapped[str | None] = mapped_column(String(32))
    notification_preferences: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    working_days: Mapped[list | None] = mapped_column(JSONB, default=list)
    meals: Mapped[dict | None] = mapped_column(JSONB)
    scheduling_style: Mapped[SchedulingStyle | None] = mapped_column(
        Enum(SchedulingStyle, values_callable=lambda x: [e.value for e in x]),
        default=SchedulingStyle.FLEXIBLE,
    )
    default_buffer_time_minutes: Mapped[int] = mapped_column(Integer, default=15)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="preferences")


# ─── UserStats ─────────────────────────────────────────────────────────


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="stats")


# ─── HabitProfile ──────────────────────────────────────────────────────


class HabitProfile(Base):
    """Learned per-user scheduling preferences derived from completion history."""

    __tablename__ = "habit_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    # 0.0–1.0 rolling completion rate (exponential moving average)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    # Hour of day (0-23) the user most often starts study tasks
    preferred_study_hour: Mapped[int | None] = mapped_column(Integer)
    # Hour of day (0-23) for workout tasks
    preferred_workout_hour: Mapped[int | None] = mapped_column(Integer)
    # Average minutes tasks start late relative to scheduled time
    avg_delay_minutes: Mapped[int] = mapped_column(Integer, default=0)
    # Typical focused work session length in minutes
    focus_session_minutes: Mapped[int] = mapped_column(Integer, default=60)
    # Total task completions recorded (for weighted averaging)
    total_completions: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="habit_profile")


# ─── Schedule ──────────────────────────────────────────────────────────


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        # Fast lookup by user + date (used by get_today / get_week)
        Index("ix_schedules_user_date", "user_id", "date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, values_callable=lambda x: [e.value for e in x]),
        default=TaskPriority.MEDIUM,
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus, values_callable=lambda x: [e.value for e in x]),
        default=ScheduleStatus.ACTIVE,
    )
    category: Mapped[TaskCategory] = mapped_column(
        Enum(TaskCategory, values_callable=lambda x: [e.value for e in x]),
        default=TaskCategory.OTHER,
    )
    date: Mapped[date | None] = mapped_column(Date, index=True)
    generated_schedule: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="schedules")


# ─── Task ──────────────────────────────────────────────────────────────


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    labels: Mapped[list | None] = mapped_column(JSONB, default=list)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, values_callable=lambda x: [e.value for e in x]),
        default=TaskPriority.MEDIUM,
    )
    category: Mapped[TaskCategory] = mapped_column(
        Enum(TaskCategory, values_callable=lambda x: [e.value for e in x]),
        default=TaskCategory.OTHER,
    )
    recurrence: Mapped[str | None] = mapped_column(
        Enum(RecurrenceType, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    recurrence_rule: Mapped[dict | None] = mapped_column(JSONB)
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)
    fixed_start: Mapped[time | None] = mapped_column(Time)
    fixed_end: Mapped[time | None] = mapped_column(Time)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Legacy columns restored for TaskService compatibility during Phase 12 stabilization
    duration: Mapped[int] = mapped_column(Integer, default=60)
    travel_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, values_callable=lambda x: [e.value for e in x]),
        default=TaskStatus.PENDING,
    )
    reminder_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    schedule_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("schedules.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="tasks")
    occurrences: Mapped[list["TaskOccurrence"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


# ─── TaskOccurrence ────────────────────────────────────────────────────


class TaskOccurrence(Base):
    __tablename__ = "task_occurrences"
    __table_args__ = (
        Index("ix_task_occurrences_user_date", "user_id", "date"),
        Index("ix_task_occurrences_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, values_callable=lambda x: [e.value for e in x]),
        default=TaskStatus.PENDING,
    )
    duration: Mapped[int] = mapped_column(Integer, default=60)
    travel_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scheduled_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    task: Mapped["Task"] = relationship(back_populates="occurrences")
    user: Mapped["User"] = relationship(back_populates="task_occurrences")
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="task_occurrence", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        back_populates="task_occurrence", cascade="all, delete-orphan"
    )


# ─── Reminder ──────────────────────────────────────────────────────────


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        # Fast lookup for pending reminders due for firing
        Index("ix_reminders_fire_time", "reminder_time"),
        # Quick filter by user + sent status
        Index("ix_reminders_user_sent", "user_id", "is_sent"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    task_occurrence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_occurrences.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reminder_type: Mapped[ReminderType] = mapped_column(
        Enum(ReminderType, values_callable=lambda x: [e.value for e in x]),
        default=ReminderType.CUSTOM,
    )
    reminder_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # Recurring reminder support
    recurrence: Mapped[RecurrenceType | None] = mapped_column(
        Enum(RecurrenceType, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    recurrence_rule: Mapped[dict | None] = mapped_column(JSONB)
    # Pre-computed next fire time for recurring reminders (indexed for efficiency)
    next_fire: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_snoozed: Mapped[bool] = mapped_column(Boolean, default=False)
    snooze_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="reminders")
    task_occurrence: Mapped[Optional["TaskOccurrence"]] = relationship(back_populates="reminders")
    history: Mapped[list["ReminderHistory"]] = relationship(
        back_populates="reminder", cascade="all, delete-orphan"
    )


# ─── ReminderHistory ───────────────────────────────────────────────────


class ReminderHistory(Base):
    """Records every fire event for a reminder — sent, snoozed, dismissed, or missed."""

    __tablename__ = "reminder_history"
    __table_args__ = (
        Index("ix_reminder_history_reminder", "reminder_id", "fired_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reminder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reminders.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    fired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    outcome: Mapped[ReminderOutcome] = mapped_column(
        Enum(ReminderOutcome, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)

    reminder: Mapped["Reminder"] = relationship(back_populates="history")


# ─── PushSubscription ───────────────────────────────────────────────────


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    push_token: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="push_subscriptions")


# ─── Notification ──────────────────────────────────────────────────────


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        # Unread badge count query: user_id + is_read
        Index("ix_notifications_user_read", "user_id", "is_read"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, values_callable=lambda x: [e.value for e in x]),
        default=NotificationType.SYSTEM,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="notifications")


# ─── Routine ─────────────────────────────────────────────────────────


class Routine(Base):
    __tablename__ = "routines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[RoutineCategory] = mapped_column(
        Enum(RoutineCategory, values_callable=lambda x: [e.value for e in x]),
        default=RoutineCategory.OTHER,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, values_callable=lambda x: [e.value for e in x]),
        default=TaskPriority.MEDIUM,
    )
    frequency: Mapped[RecurrenceType | None] = mapped_column(
        Enum(RecurrenceType, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    estimated_duration: Mapped[int] = mapped_column(Integer, default=60)
    preferred_time: Mapped[time | None] = mapped_column(Time)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    parsed_data: Mapped[dict | None] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="routines")


# ─── AIAnalysis ────────────────────────────────────────────────────────


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    analysis_result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(128))
    confidence_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="ai_analyses")


# ─── ActivityLog ───────────────────────────────────────────────────────


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_task_occurrence_created", "task_occurrence_id", "created_at"),
        Index("ix_activity_logs_user", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    task_occurrence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_occurrences.id", ondelete="CASCADE"), index=True
    )
    # Direct user_id allows analytics queries without joining tasks
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    time_spent: Mapped[int | None] = mapped_column(Integer)
    # How many minutes the task started after its scheduled time
    delay_minutes: Mapped[int | None] = mapped_column(Integer)
    skipped_reason: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(ActivityStatus, values_callable=lambda x: [e.value for e in x]),
        default=ActivityStatus.STARTED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    task_occurrence: Mapped["TaskOccurrence"] = relationship(back_populates="activity_logs")


# ─── Conversation ──────────────────────────────────────────────────────


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, values_callable=lambda x: [e.value for e in x]),
        default=ConversationStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at",
    )
    state: Mapped[Optional["ConversationState"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", uselist=False
    )


# ─── ConversationMessage ───────────────────────────────────────────────


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


# ─── ConversationState ─────────────────────────────────────────────────


class ConversationState(Base):
    __tablename__ = "conversation_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    current_state: Mapped[str] = mapped_column(String(64), default="DEFAULT")
    missing_fields: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="state")


# ─── RevokedToken ──────────────────────────────────────────────────────

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    token: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
