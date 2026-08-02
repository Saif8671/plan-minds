from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TaskCategory, TaskStatus
from app.repositories.activity_repository import ActivityLogRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.analytics import CategoryBreakdown, DashboardAnalytics, PeriodAnalytics
from app.services.ai.suggestion_service import AISuggestionService


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.task_repo = TaskRepository(db)
        self.activity_repo = ActivityLogRepository(db)
        self.user_repo = UserRepository(db)
        self.suggestion_service = AISuggestionService()

    async def get_dashboard(self, user_id: UUID) -> DashboardAnalytics:
        tasks = await self.task_repo.get_by_user(user_id, limit=1000)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        missed = sum(1 for t in tasks if t.status == TaskStatus.SKIPPED)
        completion_rate = (completed / total * 100) if total else 0.0

        study_minutes = sum(
            t.duration
            for t in tasks
            if t.category == TaskCategory.STUDY and t.status == TaskStatus.COMPLETED
        )
        focus_minutes = sum(
            t.duration for t in tasks if t.status == TaskStatus.COMPLETED
        )

        category_map: dict[str, dict] = {}
        for task in tasks:
            if task.status != TaskStatus.COMPLETED:
                continue
            cat = task.category.value
            if cat not in category_map:
                category_map[cat] = {"hours": 0.0, "count": 0}
            category_map[cat]["hours"] += task.duration / 60
            category_map[cat]["count"] += 1

        breakdown = [
            CategoryBreakdown(category=k, hours=v["hours"], task_count=v["count"])
            for k, v in category_map.items()
        ]

        user = await self.user_repo.get_by_id(user_id)
        avg_sleep = None
        if user and user.wake_time and user.sleep_time:
            wake_mins = user.wake_time.hour * 60 + user.wake_time.minute
            sleep_mins = user.sleep_time.hour * 60 + user.sleep_time.minute
            if sleep_mins > wake_mins:
                avg_sleep = (sleep_mins - wake_mins) / 60
            else:
                avg_sleep = (24 * 60 - wake_mins + sleep_mins) / 60

        consistency = min(
            100.0, completion_rate * 0.7 + (100 - (missed / max(total, 1) * 100)) * 0.3
        )
        suggestions = self.suggestion_service.generate_suggestions(tasks)

        return DashboardAnalytics(
            completion_rate=round(completion_rate, 1),
            focus_hours=round(focus_minutes / 60, 1),
            study_hours=round(study_minutes / 60, 1),
            average_sleep_hours=round(avg_sleep, 1) if avg_sleep else None,
            missed_tasks=missed,
            consistency_score=round(consistency, 1),
            total_tasks=total,
            completed_tasks=completed,
            category_breakdown=breakdown,
        )

    async def get_weekly(self, user_id: UUID) -> PeriodAnalytics:
        return await self._period_analytics(user_id, days=7, period_label="weekly")

    async def get_monthly(self, user_id: UUID) -> PeriodAnalytics:
        return await self._period_analytics(user_id, days=30, period_label="monthly")

    async def _period_analytics(
        self, user_id: UUID, days: int, period_label: str
    ) -> PeriodAnalytics:
        end = date.today()
        start = end - timedelta(days=days - 1)
        tasks = await self.task_repo.get_by_user(user_id, limit=5000)

        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        missed = sum(1 for t in tasks if t.status == TaskStatus.SKIPPED)
        completion_rate = (completed / total * 100) if total else 0.0

        focus_minutes = sum(
            t.duration for t in tasks if t.status == TaskStatus.COMPLETED
        )
        study_minutes = sum(
            t.duration
            for t in tasks
            if t.category == TaskCategory.STUDY and t.status == TaskStatus.COMPLETED
        )

        daily_breakdown = []
        for i in range(days):
            day = start + timedelta(days=i)
            day_tasks = [t for t in tasks if t.created_at.date() == day]
            day_completed = sum(
                1 for t in day_tasks if t.status == TaskStatus.COMPLETED
            )
            daily_breakdown.append(
                {
                    "date": day.isoformat(),
                    "total": len(day_tasks),
                    "completed": day_completed,
                    "rate": (
                        round(day_completed / len(day_tasks) * 100, 1)
                        if day_tasks
                        else 0
                    ),
                }
            )

        consistency = min(
            100.0, completion_rate * 0.7 + (100 - (missed / max(total, 1) * 100)) * 0.3
        )
        insights = self._generate_insights(completion_rate, missed, study_minutes / 60)

        return PeriodAnalytics(
            period=period_label,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            completion_rate=round(completion_rate, 1),
            focus_hours=round(focus_minutes / 60, 1),
            study_hours=round(study_minutes / 60, 1),
            missed_tasks=missed,
            consistency_score=round(consistency, 1),
            daily_breakdown=daily_breakdown,
            insights=insights,
        )

    def _generate_insights(
        self, completion_rate: float, missed: int, study_hours: float
    ) -> list[str]:
        insights = []
        if completion_rate >= 80:
            insights.append(
                "Great consistency! You're completing most of your scheduled tasks."
            )
        elif completion_rate >= 50:
            insights.append(
                "Moderate completion rate. Consider reducing task load or adjusting priorities."
            )
        else:
            insights.append(
                "Low completion rate. Try scheduling fewer flexible tasks per day."
            )

        if missed > 5:
            insights.append(
                f"You skipped {missed} tasks. Use regenerate schedule to replan."
            )

        if study_hours < 5:
            insights.append(
                "Study hours are below 5h. Block dedicated focus time in your schedule."
            )
        elif study_hours >= 10:
            insights.append(
                "Strong study focus this period. Remember to balance with rest."
            )

        return insights
