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


class ScoredTaskScheduler(PipelineComponent):
    """Places flexible tasks by scoring every available 15-min slot.

    Score components (all additive):
    - Priority:          urgent=40, high=30, medium=20, low=10
    - Deadline urgency:  up to 30 points (more urgent = closer deadline)
    - Energy:            morning > afternoon slump > evening recovery
    - Preferred time:    bonus if slot matches HabitProfile preferred hour
    - Load penalty:      -10 if day already ≥70% full
    """

    ENERGY_MAP = {  # hour_of_day → energy score (0-20)
        **{h: 18 for h in range(6, 10)},    # Early morning: high
        **{h: 15 for h in range(10, 12)},   # Late morning: good
        **{h: 8  for h in range(12, 14)},   # Post-lunch dip
        **{h: 14 for h in range(14, 18)},   # Afternoon: decent
        **{h: 12 for h in range(18, 21)},   # Evening: moderate
        **{h: 5  for h in range(21, 24)},   # Night: low
    }

    def process(self, context: ScheduleContext, tasks: List[Task]) -> None:
        flexible_tasks = [t for t in tasks if not t.is_fixed and not t.is_recurring]
        recurring_flex = [t for t in tasks if not t.is_fixed and t.is_recurring]
        for rt in recurring_flex:
            occurrences = RecurrenceExpander.expand_task_for_date(rt, context.target_date)
            if occurrences:
                flexible_tasks.append(rt)

        day_start = datetime.combine(context.target_date, context.wake)
        day_end = datetime.combine(context.target_date, context.sleep)
        if day_end <= day_start:
            day_end += timedelta(days=1)

        total_available = (day_end - day_start).total_seconds() / 60
        scheduled_minutes = sum(
            (datetime.combine(context.target_date, b.end) -
             datetime.combine(context.target_date, b.start)).total_seconds() / 60
            for b in context.blocks
        )
        load_ratio = scheduled_minutes / max(total_available, 1)

        # Sort by priority then deadline for tiebreaking
        flexible_sorted = sorted(
            flexible_tasks,
            key=lambda t: (
                PRIORITY_ORDER.get(
                    t.priority.value if hasattr(t.priority, "value")
                    else str(t.priority).lower(), 99
                ),
                t.deadline or datetime.max,
            ),
        )

        work_minutes = 0
        break_duration = context.prefs.break_duration_minutes if context.prefs else 15
        habit_profile = getattr(context, "habit_profile", None)

        for task in flexible_sorted:
            duration = timedelta(minutes=task.duration or 0)
            travel = timedelta(minutes=task.travel_time_minutes or 0)

            best_slot: datetime | None = None
            best_score: float = -1.0

            # Evaluate every 15-min candidate slot
            candidate = day_start
            while candidate + duration + travel <= day_end:
                start_t = (candidate + travel).time()
                end_t = (candidate + travel + duration).time()

                if not context.time_in_range(start_t) or context.has_conflict(start_t, end_t):
                    candidate += timedelta(minutes=15)
                    continue

                score = self._score_slot(task, candidate, load_ratio, habit_profile)
                if score > best_score:
                    best_score = score
                    best_slot = candidate

                candidate += timedelta(minutes=15)

            if best_slot is not None:
                placed_start = (best_slot + travel).time()
                placed_end = (best_slot + travel + duration).time()
                context.blocks.append(
                    ScheduleBlock(
                        title=task.title,
                        start=placed_start,
                        end=placed_end,
                        task_id=task.id,
                        category=task.category.value,
                        is_fixed=False,
                        score=round(best_score, 2),
                    )
                )
                work_minutes += task.duration or 0

                if work_minutes >= 90 and break_duration > 0:
                    break_cursor = datetime.combine(context.target_date, placed_end)
                    break_start = break_cursor.time()
                    break_end = (break_cursor + timedelta(minutes=break_duration)).time()
                    if context.time_in_range(break_start) and not context.has_conflict(break_start, break_end):
                        context.blocks.append(
                            ScheduleBlock(
                                title="Break",
                                start=break_start,
                                end=break_end,
                                category="personal",
                                is_fixed=False,
                            )
                        )
                    work_minutes = 0
            else:
                context.unscheduled.append(task.title)

        context.blocks.sort(key=lambda b: b.start)

    def _score_slot(
        self, task: Task, slot_start: datetime, load_ratio: float, habit_profile
    ) -> float:
        score = 0.0

        # 1. Priority score
        priority_scores = {"urgent": 40.0, "high": 30.0, "medium": 20.0, "low": 10.0}
        pval = task.priority.value if hasattr(task.priority, "value") else str(task.priority).lower()
        score += priority_scores.get(pval, 10.0)

        # 2. Deadline urgency (0–30 points)
        if task.deadline:
            hours_until = max(0, (task.deadline - slot_start).total_seconds() / 3600)
            if hours_until < 4:
                score += 30
            elif hours_until < 24:
                score += 20
            elif hours_until < 72:
                score += 10

        # 3. Energy score (0–20)
        hour = slot_start.hour
        score += self.ENERGY_MAP.get(hour, 10)

        # 4. Preferred time bonus (0–15)
        if habit_profile:
            from app.models import TaskCategory
            if task.category == TaskCategory.STUDY and habit_profile.preferred_study_hour is not None:
                diff = abs(hour - habit_profile.preferred_study_hour)
                score += max(0, 15 - diff * 3)
            elif task.category == TaskCategory.HEALTH and habit_profile.preferred_workout_hour is not None:
                diff = abs(hour - habit_profile.preferred_workout_hour)
                score += max(0, 15 - diff * 3)

        # 5. Load penalty
        if load_ratio >= 0.7:
            score -= 10

        return score


# Keep FlexibleTaskScheduler as an alias for backwards compatibility
FlexibleTaskScheduler = ScoredTaskScheduler
