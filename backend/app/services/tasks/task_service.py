"""Task service — all task business logic.

Clean separation of concerns:
- _handle_recurrence()  — creates the next recurring instance
- _sync_reminder()      — creates/updates/deletes the linked reminder
- complete_task()       — records activity + awards XP
- start_task()          — marks IN_PROGRESS, opens ActivityLog entry
- skip_task()           — marks SKIPPED, logs reason, optionally reschedules
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models import (
    ActivityLog,
    ActivityStatus,
    RecurrenceType,
    Reminder,
    ReminderType,
    Task,
    TaskStatus,
)
from app.repositories.activity_repository import ActivityLogRepository
from app.repositories.reminder_repository import ReminderRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskSkipRequest, TaskUpdate
from app.services.gamification.xp_service import GamificationService


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.reminder_repo = ReminderRepository(db)
        self.activity_repo = ActivityLogRepository(db)

    # ─── Create ───────────────────────────────────────────────────────

    async def create_task(self, user_id: UUID, data: TaskCreate) -> TaskResponse:
        """Create a task, validating fixed-time constraints and auto-creating a reminder."""
        if data.is_fixed and (not data.fixed_start or not data.fixed_end):
            raise ValidationError("Fixed tasks require fixed_start and fixed_end")

        task = Task(user_id=user_id, **data.model_dump())
        task = await self.task_repo.create(task)

        if task.reminder_time:
            await self._create_reminder(user_id, task)

        return TaskResponse.model_validate(task)

    # ─── Read ─────────────────────────────────────────────────────────

    async def get_tasks(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status=None,
    ) -> tuple[list[TaskResponse], int]:
        tasks = await self.task_repo.get_by_user(user_id, skip, limit, status)
        total = await self.task_repo.count_by_user(user_id, status)
        return [TaskResponse.model_validate(t) for t in tasks], total

    async def get_task(self, user_id: UUID, task_id: UUID) -> TaskResponse:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
        return TaskResponse.model_validate(task)

    # ─── Update ───────────────────────────────────────────────────────

    async def update_task(
        self, user_id: UUID, task_id: UUID, data: TaskUpdate
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")

        update_data = data.model_dump(exclude_unset=True)
        was_completed = task.completed

        for field, value in update_data.items():
            setattr(task, field, value)

        # Spawn next recurring instance when task is newly completed
        if task.completed and not was_completed and task.is_recurring and task.recurrence:
            await self._handle_recurrence(user_id, task)

        task = await self.task_repo.update(task)

        # Sync linked reminder if reminder_time changed
        if "reminder_time" in update_data:
            await self._sync_reminder(user_id, task)

        return TaskResponse.model_validate(task)

    # ─── Delete ───────────────────────────────────────────────────────

    async def delete_task(self, user_id: UUID, task_id: UUID) -> None:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
        await self.task_repo.delete(task)

    # ─── Lifecycle transitions ────────────────────────────────────────

    async def start_task(self, user_id: UUID, task_id: UUID) -> TaskResponse:
        """Mark a task as IN_PROGRESS and open an ActivityLog entry."""
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
        if task.status == TaskStatus.COMPLETED:
            raise ValidationError("Task is already completed")

        task.status = TaskStatus.IN_PROGRESS
        task = await self.task_repo.update(task)

        activity = ActivityLog(
            task_id=task_id,
            user_id=user_id,
            started_at=datetime.now(UTC),
            status=ActivityStatus.STARTED,
        )
        await self.activity_repo.create(activity)

        return TaskResponse.model_validate(task)

    async def complete_task(self, user_id: UUID, task_id: UUID) -> TaskResponse:
        """Complete a task: update status, compute actual duration, award XP."""
        update_data = TaskUpdate(completed=True, status=TaskStatus.COMPLETED)
        task_response = await self.update_task(user_id, task_id, update_data)

        # Compute actual time spent from most recent started ActivityLog
        actual_duration = task_response.duration
        result = await self.db.execute(
            select(ActivityLog)
            .where(
                ActivityLog.task_id == task_id,
                ActivityLog.status == ActivityStatus.STARTED,
                ActivityLog.started_at.isnot(None),
            )
            .order_by(ActivityLog.started_at.desc())
            .limit(1)
        )
        open_log = result.scalar_one_or_none()

        now = datetime.now(UTC)
        if open_log and open_log.started_at:
            started_at = open_log.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=UTC)
            elapsed = int((now - started_at).total_seconds() / 60)
            actual_duration = max(elapsed, 1)
            open_log.completed_at = now
            open_log.time_spent = actual_duration
            open_log.status = ActivityStatus.COMPLETED
            await self.activity_repo.update(open_log)
        else:
            # Fallback: no open log → create a completion record
            activity = ActivityLog(
                task_id=task_id,
                user_id=user_id,
                time_spent=actual_duration,
                status=ActivityStatus.COMPLETED,
                completed_at=now,
            )
            await self.activity_repo.create(activity)

        # Award XP (silent — no transaction commit inside service)
        task_model = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if task_model:
            gamification = GamificationService(self.db)
            await gamification.award_task_completion_xp(user_id, task_model)

        return task_response

    async def skip_task(
        self,
        user_id: UUID,
        task_id: UUID,
        reason: str | None = None,
    ) -> TaskResponse:
        """Mark a task as SKIPPED and log the reason."""
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
        if task.status == TaskStatus.COMPLETED:
            raise ValidationError("Cannot skip a completed task")

        task.status = TaskStatus.SKIPPED
        task = await self.task_repo.update(task)

        activity = ActivityLog(
            task_id=task_id,
            user_id=user_id,
            status=ActivityStatus.SKIPPED,
            skipped_reason=reason,
            completed_at=datetime.now(UTC),
        )
        await self.activity_repo.create(activity)

        return TaskResponse.model_validate(task)

    # ─── Activity logging ─────────────────────────────────────────────

    async def log_activity(self, user_id: UUID, task_id: UUID, time_spent: int) -> dict:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")

        activity = ActivityLog(
            task_id=task_id,
            user_id=user_id,
            time_spent=time_spent,
            status=ActivityStatus.COMPLETED,
            completed_at=datetime.now(UTC),
        )
        await self.activity_repo.create(activity)
        return {"message": "Activity logged successfully"}

    # ─── Private helpers ──────────────────────────────────────────────

    async def _handle_recurrence(self, user_id: UUID, task: Task) -> None:
        """Spawn the next recurring instance of a task after completion."""
        delta_map = {
            RecurrenceType.DAILY: timedelta(days=1),
            RecurrenceType.WEEKLY: timedelta(days=7),
            RecurrenceType.MONTHLY: timedelta(days=30),
        }
        delta = delta_map.get(task.recurrence, timedelta(days=1))  # type: ignore[arg-type]

        next_deadline = task.deadline + delta if task.deadline else None
        next_reminder = task.reminder_time + delta if task.reminder_time else None

        new_task = Task(
            user_id=user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            category=task.category,
            duration=task.duration,
            travel_time_minutes=task.travel_time_minutes,
            deadline=next_deadline,
            reminder_time=next_reminder,
            recurrence=task.recurrence,
            recurrence_rule=task.recurrence_rule,
            is_fixed=task.is_fixed,
            fixed_start=task.fixed_start,
            fixed_end=task.fixed_end,
            is_recurring=task.is_recurring,
            status=TaskStatus.PENDING,
        )
        new_task = await self.task_repo.create(new_task)

        if new_task.reminder_time:
            await self._create_reminder(user_id, new_task)

    def _make_reminder(self, user_id: UUID, task: Task) -> Reminder:
        return Reminder(
            user_id=user_id,
            task_id=task.id,
            title=f"Reminder: {task.title}",
            reminder_type=ReminderType.TASK,
            reminder_time=task.reminder_time,  # type: ignore[arg-type]
            message=task.description or f"It's time for {task.title}",
        )

    async def _create_reminder(self, user_id: UUID, task: Task) -> None:
        await self.reminder_repo.create(self._make_reminder(user_id, task))

    async def _sync_reminder(self, user_id: UUID, task: Task) -> None:
        """Create, update, or delete the reminder linked to a task's reminder_time."""
        result = await self.db.execute(
            select(Reminder).where(Reminder.task_id == task.id)
        )
        existing = result.scalar_one_or_none()

        if task.reminder_time:
            if existing:
                existing.reminder_time = task.reminder_time
                existing.is_sent = False
                await self.reminder_repo.update(existing)
            else:
                await self._create_reminder(user_id, task)
        elif existing:
            await self.reminder_repo.delete(existing)
