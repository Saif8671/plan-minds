from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import TaskCategory, TaskOccurrence, TaskStatus, User
from app.schemas.analytics import CategoryBreakdown, DashboardAnalytics, PeriodAnalytics


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, user_id: UUID) -> DashboardAnalytics:
        thirty_days_ago = date.today() - timedelta(days=30)
        stmt = (
            select(TaskOccurrence)
            .join(TaskOccurrence.task)
            .where(
                TaskOccurrence.user_id == user_id,
                TaskOccurrence.date >= thirty_days_ago,
            )
            .options(joinedload(TaskOccurrence.task))
        )

        result = await self.db.execute(stmt)
        occurrences = result.scalars().all()

        total = len(occurrences)
        completed = sum(1 for o in occurrences if o.status == TaskStatus.COMPLETED)
        missed = sum(1 for o in occurrences if o.status == TaskStatus.SKIPPED)
        completion_rate = (completed / total * 100) if total else 0.0

        study_minutes = sum(
            o.duration
            for o in occurrences
            if o.task.category == TaskCategory.STUDY
            and o.status == TaskStatus.COMPLETED
        )
        focus_minutes = sum(
            o.duration for o in occurrences if o.status == TaskStatus.COMPLETED
        )

        category_map = {}
        for o in occurrences:
            if o.status != TaskStatus.COMPLETED:
                continue
            cat = o.task.category.value
            if cat not in category_map:
                category_map[cat] = {"hours": 0.0, "count": 0}
            category_map[cat]["hours"] += o.duration / 60
            category_map[cat]["count"] += 1

        breakdown = [
            CategoryBreakdown(category=k, hours=v["hours"], task_count=v["count"])
            for k, v in category_map.items()
        ]

        user_stmt = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

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

        stmt = (
            select(TaskOccurrence)
            .join(TaskOccurrence.task)
            .where(
                TaskOccurrence.user_id == user_id,
                TaskOccurrence.date >= start,
                TaskOccurrence.date <= end,
            )
            .options(joinedload(TaskOccurrence.task))
        )

        result = await self.db.execute(stmt)
        occurrences = result.scalars().all()

        total = len(occurrences)
        completed = sum(1 for o in occurrences if o.status == TaskStatus.COMPLETED)
        missed = sum(1 for o in occurrences if o.status == TaskStatus.SKIPPED)
        completion_rate = (completed / total * 100) if total else 0.0

        focus_minutes = sum(
            o.duration for o in occurrences if o.status == TaskStatus.COMPLETED
        )
        study_minutes = sum(
            o.duration
            for o in occurrences
            if o.task.category == TaskCategory.STUDY
            and o.status == TaskStatus.COMPLETED
        )

        daily_breakdown = []
        for i in range(days):
            day = start + timedelta(days=i)
            day_occurrences = [o for o in occurrences if o.date == day]
            day_completed = sum(
                1 for o in day_occurrences if o.status == TaskStatus.COMPLETED
            )
            daily_breakdown.append(
                {
                    "date": day.isoformat(),
                    "total": len(day_occurrences),
                    "completed": day_completed,
                    "rate": (
                        round(day_completed / len(day_occurrences) * 100, 1)
                        if day_occurrences
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

    async def generate_weekly_report_markdown(self, user_id: UUID) -> str:
        weekly = await self.get_weekly(user_id)

        lines = [
            "# Weekly Performance Report",
            f"**Date Range:** {weekly.start_date} to {weekly.end_date}",
            "---",
            "## Summary",
            f"- **Completion Rate:** {weekly.completion_rate}%",
            f"- **Focus Hours:** {weekly.focus_hours}h",
            f"- **Study Hours:** {weekly.study_hours}h",
            f"- **Missed Tasks:** {weekly.missed_tasks}",
            f"- **Consistency Score:** {weekly.consistency_score}/100",
            "",
            "## Daily Breakdown",
        ]

        for day in weekly.daily_breakdown:
            lines.append(
                f"- **{day['date']}:** {day['completed']}/{day['total']} tasks ({day['rate']}%)"
            )

        lines.append("")
        lines.append("## Insights & Recommendations")

        if weekly.insights:
            for insight in weekly.insights:
                lines.append(f"- {insight}")
        else:
            lines.append("- Keep up the good work!")

        return "\n".join(lines)
