import asyncio
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
    UserPreferences,
)
from app.repositories.preferences_repository import PreferencesRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.schedule import (
    GeneratedSchedule,
    ScheduleBlock,
    ScheduleGenerateRequest,
    ScheduleGenerateMultiRequest,
    ScheduleRegenerateRequest,
    ScheduleResponse,
)
from app.services.scheduling.conflict_resolution import ConflictResolutionService

from app.services.scheduling.pipeline import (
    ScheduleContext,
    MealScheduler,
    WorkCollegeScheduler,
    FixedTaskScheduler,
    FlexibleTaskScheduler,
)


class SchedulingEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.schedule_repo = ScheduleRepository(db)
        self.prefs_repo = PreferencesRepository(db)

    async def generate(
        self, user: User, data: ScheduleGenerateRequest
    ) -> ScheduleResponse:
        target_date = data.target_date or date.today()
        
        # Load tasks and preferences concurrently
        tasks, prefs = await asyncio.gather(
            self.task_repo.get_pending_for_user(user.id),
            self.prefs_repo.get_by_user(user.id)
        )

        if data.include_parsed_routine:
            tasks = self._merge_parsed_routine(
                tasks, data.include_parsed_routine, user.id
            )

        wake = user.wake_time or time(6, 0)
        sleep = user.sleep_time or time(23, 0)
        break_duration = 15

        if prefs:
            wake = prefs.wake_time or wake
            sleep = prefs.sleep_time or sleep
            break_duration = prefs.break_duration_minutes or break_duration

        if data.include_parsed_routine:
            if data.include_parsed_routine.wake_time:
                wake = data.include_parsed_routine.wake_time
            if data.include_parsed_routine.sleep_time:
                sleep = data.include_parsed_routine.sleep_time

        generated = self._build_schedule(
            tasks, target_date, wake, sleep, break_duration, prefs
        )
        return await self._persist_schedule(user.id, target_date, generated)

    async def generate_multi_day(
        self, user: User, data: ScheduleGenerateMultiRequest
    ) -> list[ScheduleResponse]:
        start_date = data.start_date or date.today()
        
        # Load tasks and preferences concurrently
        tasks, prefs = await asyncio.gather(
            self.task_repo.get_pending_for_user(user.id),
            self.prefs_repo.get_by_user(user.id)
        )
        wake = user.wake_time or time(6, 0)
        sleep = user.sleep_time or time(23, 0)
        break_duration = 15
        
        if prefs:
            wake = prefs.wake_time or wake
            sleep = prefs.sleep_time or sleep
            break_duration = prefs.break_duration_minutes or break_duration
            
        responses = []
        
        for i in range(data.days):
            current_date = start_date + timedelta(days=i)
            
            generated = self._build_schedule(
                tasks, current_date, wake, sleep, break_duration, prefs
            )
            resp = await self._persist_schedule(user.id, current_date, generated)
            responses.append(resp)
            
            # Remove successfully placed non-recurring flexible tasks so they aren't scheduled again tomorrow
            placed_task_ids = {
                b.task_id for b in generated.blocks 
                if b.task_id and not getattr(next((t for t in tasks if t.id == b.task_id), None), 'is_recurring', False)
            }
            
            tasks = [t for t in tasks if getattr(t, 'is_recurring', False) or t.id not in placed_task_ids]

        return responses

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
        break_duration: int = 15,
        prefs: UserPreferences | None = None,
    ) -> GeneratedSchedule:
        context = ScheduleContext(target_date, wake, sleep, prefs)
        
        pipeline = [
            MealScheduler(),
            WorkCollegeScheduler(),
            FixedTaskScheduler(),
            FlexibleTaskScheduler(),
        ]
        
        for component in pipeline:
            component.process(context, tasks)

        generated = GeneratedSchedule(
            date=target_date,
            wake_time=wake,
            sleep_time=sleep,
            blocks=context.blocks,
            unscheduled_tasks=context.unscheduled,
            metadata={
                "total_blocks": len(context.blocks),
                "unscheduled_count": len(context.unscheduled),
                "break_duration": break_duration,
            },
        )
        
        generated.suggestions = ConflictResolutionService.analyze_schedule(generated)
        
        return generated

    def _time_in_range(self, t: time, start: time, end: time) -> bool:
        """Check if time t falls within [start, end] range."""
        if start <= end:
            return start <= t <= end
        # Handles overnight ranges (e.g., 22:00 to 06:00)
        return t >= start or t <= end

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
