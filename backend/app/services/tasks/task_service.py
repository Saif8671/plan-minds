from datetime import datetime, timedelta, UTC
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
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.gamification.xp_service import GamificationService


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.reminder_repo = ReminderRepository(db)
        self.activity_repo = ActivityLogRepository(db)

    async def create_task(self, user_id: UUID, data: TaskCreate) -> TaskResponse:
        if data.is_fixed and (not data.fixed_start or not data.fixed_end):
            raise ValidationError("Fixed tasks require fixed_start and fixed_end")

        task = Task(user_id=user_id, **data.model_dump())
        task = await self.task_repo.create(task)

        if task.reminder_time:
            reminder = Reminder(
                user_id=user_id,
                task_id=task.id,
                title=f"Reminder: {task.title}",
                reminder_type=ReminderType.TASK,
                reminder_time=task.reminder_time,
                message=task.description or f"It's time for {task.title}"
            )
            await self.reminder_repo.create(reminder)

        return TaskResponse.model_validate(task)

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

        # Handle recurrence logic when task is newly marked as completed
        if task.completed and not was_completed and task.is_recurring and task.recurrence:
            # Create a new instance
            next_deadline = None
            next_reminder = None
            delta = timedelta(days=1)
            
            if task.recurrence == RecurrenceType.DAILY:
                delta = timedelta(days=1)
            elif task.recurrence == RecurrenceType.WEEKLY:
                delta = timedelta(days=7)
            elif task.recurrence == RecurrenceType.MONTHLY:
                delta = timedelta(days=30)
                
            if task.deadline:
                next_deadline = task.deadline + delta
            if task.reminder_time:
                next_reminder = task.reminder_time + delta

            new_task = Task(
                user_id=task.user_id,
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
                reminder = Reminder(
                    user_id=user_id,
                    task_id=new_task.id,
                    title=f"Reminder: {new_task.title}",
                    reminder_type=ReminderType.TASK,
                    reminder_time=new_task.reminder_time,
                    message=new_task.description or f"It's time for {new_task.title}"
                )
                await self.reminder_repo.create(reminder)

        task = await self.task_repo.update(task)

        # Handle reminder updates for the current task
        if "reminder_time" in update_data:
            result = await self.db.execute(
                select(Reminder).where(Reminder.task_id == task.id)
            )
            existing_reminder = result.scalar_one_or_none()

            if task.reminder_time:
                if existing_reminder:
                    existing_reminder.reminder_time = task.reminder_time
                    existing_reminder.is_sent = False
                    await self.reminder_repo.update(existing_reminder)
                else:
                    reminder = Reminder(
                        user_id=user_id,
                        task_id=task.id,
                        title=f"Reminder: {task.title}",
                        reminder_type=ReminderType.TASK,
                        reminder_time=task.reminder_time,
                        message=task.description or f"It's time for {task.title}"
                    )
                    await self.reminder_repo.create(reminder)
            elif existing_reminder:
                await self.reminder_repo.delete(existing_reminder)

        return TaskResponse.model_validate(task)

    async def delete_task(self, user_id: UUID, task_id: UUID) -> None:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
        await self.task_repo.delete(task)

    async def complete_task(self, user_id: UUID, task_id: UUID) -> TaskResponse:
        # We reuse update_task to leverage the recurrence logic
        update_data = TaskUpdate(completed=True, status=TaskStatus.COMPLETED)
        task_response = await self.update_task(user_id, task_id, update_data)
        
        # Log activity
        activity = ActivityLog(
            task_id=task_id,
            time_spent=task_response.duration,
            status=ActivityStatus.COMPLETED,
            completed_at=datetime.now(UTC),
        )
        await self.activity_repo.create(activity)
        
        # Award XP
        task_model = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if task_model:
            gamification = GamificationService(self.db)
            xp_result = await gamification.award_task_completion_xp(user_id, task_model)
            # We can attach the xp_result to the response if we extend the schema, 
            # or just let it run silently. For now, it runs silently.
        
        return task_response

    async def log_activity(self, user_id: UUID, task_id: UUID, time_spent: int) -> dict:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
            
        activity = ActivityLog(
            task_id=task_id,
            time_spent=time_spent,
            status=ActivityStatus.COMPLETED,
            completed_at=datetime.now(UTC),
        )
        await self.activity_repo.create(activity)
        return {"message": "Activity logged successfully"}
