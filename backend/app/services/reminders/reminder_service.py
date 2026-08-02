from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Reminder, ReminderType, Task, User
from app.repositories.reminder_repository import ReminderRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate


class ReminderService:
    def __init__(self, db: AsyncSession):
        self.reminder_repo = ReminderRepository(db)
        self.task_repo = TaskRepository(db)

    async def create_reminder(
        self, user_id: UUID, data: ReminderCreate
    ) -> ReminderResponse:
        reminder = Reminder(user_id=user_id, **data.model_dump())
        reminder = await self.reminder_repo.create(reminder)
        return ReminderResponse.model_validate(reminder)

    async def get_reminders(
        self, user_id: UUID, skip: int = 0, limit: int = 100, include_sent: bool = True
    ) -> list[ReminderResponse]:
        reminders = await self.reminder_repo.get_by_user(
            user_id, skip, limit, include_sent
        )
        return [ReminderResponse.model_validate(r) for r in reminders]

    async def update_reminder(
        self, user_id: UUID, reminder_id: UUID, data: ReminderUpdate
    ) -> ReminderResponse:
        reminder = await self.reminder_repo.get_by_id_and_user(reminder_id, user_id)
        if not reminder:
            raise NotFoundError("Reminder")
        
        update_data = data.model_dump(exclude_unset=True)
        reminder = await self.reminder_repo.update(reminder, obj_in=update_data)
        return ReminderResponse.model_validate(reminder)

    async def delete_reminder(self, user_id: UUID, reminder_id: UUID) -> None:
        reminder = await self.reminder_repo.get_by_id_and_user(reminder_id, user_id)
        if not reminder:
            raise NotFoundError("Reminder")
        await self.reminder_repo.delete(reminder)

    async def generate_task_reminders(
        self, user: User, tasks: list[Task]
    ) -> list[ReminderResponse]:
        prefs = user.reminder_preferences or {}
        lead_minutes = prefs.get("task_lead_minutes", 15)
        created: list[ReminderResponse] = []

        for task in tasks:
            if task.is_fixed and task.fixed_start:
                reminder_time = datetime.combine(
                    datetime.today(), task.fixed_start
                ) - timedelta(minutes=lead_minutes)
            elif task.deadline:
                reminder_time = task.deadline - timedelta(minutes=lead_minutes)
            else:
                continue

            reminder = Reminder(
                user_id=user.id,
                task_id=task.id,
                title=f"Upcoming: {task.title}",
                reminder_type=ReminderType.TASK,
                reminder_time=reminder_time,
                message=f"Your task '{task.title}' is coming up.",
            )
            reminder = await self.reminder_repo.create(reminder)
            created.append(ReminderResponse.model_validate(reminder))

        return created

    async def generate_habit_reminders(self, user: User) -> list[ReminderResponse]:
        prefs = user.reminder_preferences or {}
        created: list[ReminderResponse] = []

        habit_defaults = [
            (ReminderType.WATER, "Drink water", 120),
            (ReminderType.MEAL, "Time to eat", 240),
        ]

        if prefs.get("sleep_reminders", True) and user.sleep_time:
            habit_defaults.append((ReminderType.SLEEP, "Wind down for sleep", 0))

        base_time = datetime.now().replace(second=0, microsecond=0)
        for reminder_type, title, interval in habit_defaults:
            if reminder_type == ReminderType.SLEEP and user.sleep_time:
                reminder_time = datetime.combine(
                    datetime.today(), user.sleep_time
                ) - timedelta(minutes=30)
            else:
                reminder_time = base_time + timedelta(minutes=interval)

            reminder = Reminder(
                user_id=user.id,
                title=title,
                reminder_type=reminder_type,
                reminder_time=reminder_time,
                message=title,
            )
            reminder = await self.reminder_repo.create(reminder)
            created.append(ReminderResponse.model_validate(reminder))

        return created
