from datetime import date, datetime, time, timedelta
from typing import List

from app.models import Task, UserPreferences
from app.schemas.schedule import ScheduleBlock
from app.services.scheduling.recurrence import RecurrenceExpander

PRIORITY_ORDER = {
    "urgent": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

DEFAULT_MEALS = [
    {"title": "Breakfast", "start": time(7, 0), "end": time(7, 30), "category": "meal"},
    {"title": "Lunch", "start": time(12, 30), "end": time(13, 0), "category": "meal"},
    {"title": "Dinner", "start": time(19, 30), "end": time(20, 0), "category": "meal"},
]


class ScheduleContext:
    def __init__(self, target_date: date, wake: time, sleep: time, prefs: UserPreferences | None):
        self.target_date = target_date
        self.wake = wake
        self.sleep = sleep
        self.prefs = prefs
        self.blocks: List[ScheduleBlock] = []
        self.unscheduled: List[str] = []

    def has_conflict(self, start: time, end: time) -> bool:
        for block in self.blocks:
            if start < block.end and end > block.start:
                return True
        return False

    def time_in_range(self, t: time) -> bool:
        if self.wake <= self.sleep:
            return self.wake <= t <= self.sleep
        return t >= self.wake or t <= self.sleep


class PipelineComponent:
    def process(self, context: ScheduleContext, tasks: List[Task]) -> None:
        raise NotImplementedError


class MealScheduler(PipelineComponent):
    def process(self, context: ScheduleContext, tasks: List[Task]) -> None:
        for meal in DEFAULT_MEALS:
            if context.time_in_range(meal["start"]):
                context.blocks.append(
                    ScheduleBlock(
                        title=meal["title"],
                        start=meal["start"],
                        end=meal["end"],
                        category=meal["category"],
                        is_fixed=True,
                    )
                )


class WorkCollegeScheduler(PipelineComponent):
    def process(self, context: ScheduleContext, tasks: List[Task]) -> None:
        prefs = context.prefs
        if not prefs:
            return
        if prefs.work_start and prefs.work_end:
            context.blocks.append(
                ScheduleBlock(
                    title="Work",
                    start=prefs.work_start,
                    end=prefs.work_end,
                    category="work",
                    is_fixed=True,
                )
            )
        if prefs.college_start and prefs.college_end:
            context.blocks.append(
                ScheduleBlock(
                    title="College",
                    start=prefs.college_start,
                    end=prefs.college_end,
                    category="work",
                    is_fixed=True,
                )
            )


class FixedTaskScheduler(PipelineComponent):
    def process(self, context: ScheduleContext, tasks: List[Task]) -> None:
        fixed_tasks = [t for t in tasks if t.is_fixed and t.fixed_start and t.fixed_end and not t.is_recurring]
        
        # Also include recurring tasks that are fixed time and occur today
        recurring_fixed = [t for t in tasks if t.is_fixed and t.is_recurring and t.fixed_start and t.fixed_end]
        for rt in recurring_fixed:
            occurrences = RecurrenceExpander.expand_task_for_date(rt, context.target_date)
            if occurrences:
                fixed_tasks.append(rt)

        for task in sorted(fixed_tasks, key=lambda t: t.fixed_start):  # type: ignore
            if not context.has_conflict(task.fixed_start, task.fixed_end): # type: ignore
                context.blocks.append(
                    ScheduleBlock(
                        title=task.title,
                        start=task.fixed_start, # type: ignore
                        end=task.fixed_end, # type: ignore
                        task_id=task.id,
                        category=task.category.value,
                        is_fixed=True,
                    )
                )
            else:
                context.unscheduled.append(f"{task.title} (conflict)")


class FlexibleTaskScheduler(PipelineComponent):
    def process(self, context: ScheduleContext, tasks: List[Task]) -> None:
        flexible_tasks = [t for t in tasks if not t.is_fixed and not t.is_recurring]
        
        # Also include recurring flexible tasks that occur today
        recurring_flex = [t for t in tasks if not t.is_fixed and t.is_recurring]
        for rt in recurring_flex:
            occurrences = RecurrenceExpander.expand_task_for_date(rt, context.target_date)
            if occurrences:
                flexible_tasks.append(rt)

        cursor = datetime.combine(context.target_date, context.wake)
        day_end = datetime.combine(context.target_date, context.sleep)
        if day_end <= cursor:
            day_end += timedelta(days=1)

        flexible_sorted = sorted(
            flexible_tasks,
            key=lambda t: (
                PRIORITY_ORDER.get(t.priority.value if hasattr(t.priority, 'value') else str(t.priority).lower(), 99),
                t.deadline or datetime.max,
            ),
        )

        work_minutes = 0
        break_duration = context.prefs.break_duration_minutes if context.prefs else 15

        for task in flexible_sorted:
            duration = timedelta(minutes=task.duration or 0)
            travel = timedelta(minutes=task.travel_time_minutes or 0)
            placed = False
            search_cursor = cursor

            while search_cursor + duration + travel <= day_end:
                proposed_start = (search_cursor + travel).time()
                proposed_end = (search_cursor + travel + duration).time()

                if not context.time_in_range(proposed_start):
                    search_cursor += timedelta(minutes=15)
                    continue

                if not context.has_conflict(proposed_start, proposed_end):
                    context.blocks.append(
                        ScheduleBlock(
                            title=task.title,
                            start=proposed_start,
                            end=proposed_end,
                            task_id=task.id,
                            category=task.category.value,
                            is_fixed=False,
                        )
                    )

                    work_minutes += task.duration or 0
                    cursor = search_cursor + travel + duration + timedelta(minutes=10)

                    if work_minutes >= 90 and break_duration > 0:
                        break_start = cursor.time()
                        break_end = (cursor + timedelta(minutes=break_duration)).time()
                        if context.time_in_range(break_start):
                            context.blocks.append(
                                ScheduleBlock(
                                    title="Break",
                                    start=break_start,
                                    end=break_end,
                                    category="personal",
                                    is_fixed=False,
                                )
                            )
                            cursor += timedelta(minutes=break_duration)
                        work_minutes = 0

                    placed = True
                    break
                
                search_cursor += timedelta(minutes=15)

            if not placed:
                context.unscheduled.append(task.title)

        context.blocks.sort(key=lambda b: b.start)
