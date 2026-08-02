from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    RecurrenceType,
    Schedule,
    ScheduleStatus,
    Task,
    TaskCategory,
    TaskPriority,
    TaskStatus,
    User,
)
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.schedule import (
    GeneratedSchedule,
    ScheduleBlock,
    ScheduleGenerateRequest,
    ScheduleRegenerateRequest,
    ScheduleResponse,
)

PRIORITY_ORDER = {
    TaskPriority.URGENT: 0,
    TaskPriority.HIGH: 1,
    TaskPriority.MEDIUM: 2,
    TaskPriority.LOW: 3,
}


class SchedulingEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.schedule_repo = ScheduleRepository(db)

    async def generate(
        self, user: User, data: ScheduleGenerateRequest
    ) -> ScheduleResponse:
        target_date = data.target_date or date.today()
        tasks = await self.task_repo.get_pending_for_user(user.id)

        if data.include_parsed_routine:
            tasks = self._merge_parsed_routine(
                tasks, data.include_parsed_routine, user.id
            )

        wake = user.wake_time or time(6, 0)
        sleep = user.sleep_time or time(23, 0)

        if data.include_parsed_routine:
            if data.include_parsed_routine.wake_time:
                wake = data.include_parsed_routine.wake_time
            if data.include_parsed_routine.sleep_time:
                sleep = data.include_parsed_routine.sleep_time

        generated = self._build_schedule(tasks, target_date, wake, sleep)
        return await self._persist_schedule(user.id, target_date, generated)

    async def regenerate(
        self, user: User, data: ScheduleRegenerateRequest
    ) -> ScheduleResponse:
        target_date = data.target_date or date.today()

        for task_id in data.skipped_task_ids:
            task = await self.task_repo.get_by_id_and_user(task_id, user.id)
            if task:
                task.status = TaskStatus.SKIPPED
                await self.task_repo.update(task)

        return await self.generate(
            user, ScheduleGenerateRequest(target_date=target_date)
        )

    async def get_today(self, user_id: UUID) -> ScheduleResponse | None:
        schedule = await self.schedule_repo.get_by_user_and_date(user_id, date.today())
        if not schedule:
            return None
        return ScheduleResponse.model_validate(schedule)

    async def get_week(
        self, user_id: UUID, start: date | None = None
    ) -> list[ScheduleResponse]:
        start_date = start or date.today()
        end_date = start_date + timedelta(days=6)
        schedules = await self.schedule_repo.get_week_for_user(
            user_id, start_date, end_date
        )
        return [ScheduleResponse.model_validate(s) for s in schedules]

    def _build_schedule(
        self,
        tasks: list[Task],
        target_date: date,
        wake: time,
        sleep: time,
    ) -> GeneratedSchedule:
        blocks: list[ScheduleBlock] = []
        unscheduled: list[str] = []

        recurring_tasks = [
            t
            for t in tasks
            if t.is_recurring
            and t.recurrence
            in {RecurrenceType.DAILY, RecurrenceType.WEEKLY, RecurrenceType.MONTHLY}
        ]
        fixed_tasks = [t for t in tasks if t.is_fixed and t.fixed_start and t.fixed_end]
        flexible_tasks = [t for t in tasks if not t.is_fixed and not t.is_recurring]

        for task in sorted(fixed_tasks, key=lambda t: t.fixed_start):
            blocks.append(
                ScheduleBlock(
                    title=task.title,
                    start=task.fixed_start,
                    end=task.fixed_end,
                    task_id=task.id,
                    category=task.category.value,
                    is_fixed=True,
                )
            )

        cursor = datetime.combine(target_date, wake)
        day_end = datetime.combine(target_date, sleep)
        if day_end <= cursor:
            day_end += timedelta(days=1)

        flexible_sorted = sorted(
            [*flexible_tasks, *recurring_tasks],
            key=lambda t: (
                PRIORITY_ORDER.get(t.priority, 99),
                t.deadline or datetime.max,
            ),
        )

        for task in flexible_sorted:
            duration = timedelta(minutes=task.duration)
            placed = False

            while cursor + duration <= day_end:
                proposed_start = cursor.time()
                proposed_end = (cursor + duration).time()

                if not self._has_conflict(proposed_start, proposed_end, blocks):
                    blocks.append(
                        ScheduleBlock(
                            title=task.title,
                            start=proposed_start,
                            end=proposed_end,
                            task_id=task.id,
                            category=task.category.value,
                            is_fixed=False,
                        )
                    )
                    cursor += duration + timedelta(minutes=15)
                    placed = True
                    break

                cursor += timedelta(minutes=30)

            if not placed:
                unscheduled.append(task.title)

        blocks.sort(key=lambda b: b.start)

        return GeneratedSchedule(
            date=target_date,
            wake_time=wake,
            sleep_time=sleep,
            blocks=blocks,
            unscheduled_tasks=unscheduled,
            metadata={
                "total_blocks": len(blocks),
                "unscheduled_count": len(unscheduled),
            },
        )

    def _has_conflict(
        self, start: time, end: time, blocks: list[ScheduleBlock]
    ) -> bool:
        for block in blocks:
            if start < block.end and end > block.start:
                return True
        return False

    def _merge_parsed_routine(self, tasks, parsed, user_id: UUID) -> list[Task]:
        merged = list(tasks)

        for event in parsed.fixed_events:
            merged.append(
                Task(
                    user_id=user_id,
                    title=event.title,
                    is_fixed=True,
                    fixed_start=event.start,
                    fixed_end=event.end,
                    duration=self._duration_minutes(event.start, event.end),
                    category=TaskCategory.WORK,
                    status=TaskStatus.PENDING,
                )
            )

        for flex in parsed.flexible_tasks:
            priority_map = {
                "low": TaskPriority.LOW,
                "medium": TaskPriority.MEDIUM,
                "high": TaskPriority.HIGH,
                "urgent": TaskPriority.URGENT,
            }
            merged.append(
                Task(
                    user_id=user_id,
                    title=flex.title,
                    duration=flex.duration,
                    priority=priority_map.get(
                        flex.priority.lower(), TaskPriority.MEDIUM
                    ),
                    category=TaskCategory.STUDY,
                    status=TaskStatus.PENDING,
                )
            )

        return merged

    def _duration_minutes(self, start: time, end: time) -> int:
        start_dt = datetime.combine(date.today(), start)
        end_dt = datetime.combine(date.today(), end)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        return int((end_dt - start_dt).total_seconds() / 60)

    async def _persist_schedule(
        self, user_id: UUID, target_date: date, generated: GeneratedSchedule
    ) -> ScheduleResponse:
        existing = await self.schedule_repo.get_by_user_and_date(user_id, target_date)
        schedule_data = generated.model_dump(mode="json")

        if existing:
            existing.generated_schedule = schedule_data
            existing.title = f"Schedule for {target_date.isoformat()}"
            schedule = await self.schedule_repo.update(existing)
        else:
            wake_dt = datetime.combine(target_date, generated.wake_time or time(6, 0))
            sleep_dt = datetime.combine(
                target_date, generated.sleep_time or time(23, 0)
            )
            if sleep_dt <= wake_dt:
                sleep_dt += timedelta(days=1)

            schedule = Schedule(
                user_id=user_id,
                title=f"Schedule for {target_date.isoformat()}",
                date=target_date,
                start_time=wake_dt,
                end_time=sleep_dt,
                status=ScheduleStatus.ACTIVE,
                generated_schedule=schedule_data,
            )
            schedule = await self.schedule_repo.create(schedule)

        return ScheduleResponse.model_validate(schedule)
