"""Habit learning service — tracks user completion patterns and infers preferences.

Updates HabitProfile after each task completion using exponential moving averages.
Generates proactive suggestions based on learned patterns.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import HabitProfile, Task, TaskCategory


class HabitService:
    # EMA smoothing factor: 0.2 = 20% new observation weight, 80% history weight
    _ALPHA = 0.2

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: UUID) -> HabitProfile:
        """Get or create the user's habit profile."""
        result = await self.db.execute(
            select(HabitProfile).where(HabitProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = HabitProfile(user_id=user_id)
            self.db.add(profile)
            await self.db.flush()
            await self.db.refresh(profile)
        return profile

    async def update_profile(
        self,
        user_id: UUID,
        completed_task: Task,
        completed_at: datetime | None = None,
        delay_minutes: int | None = None,
    ) -> HabitProfile:
        """Update running habit metrics after a task is completed.

        Does NOT commit — caller owns the transaction.
        """
        profile = await self.get_profile(user_id)
        now = completed_at or datetime.now(UTC)
        profile.total_completions += 1

        # Completion rate: EMA toward 1.0 (completed)
        profile.completion_rate = (
            self._ALPHA * 1.0 + (1 - self._ALPHA) * profile.completion_rate
        )

        # Preferred hour by category (hour of day when task was completed)
        hour = now.hour
        if completed_task.category == TaskCategory.STUDY:
            if profile.preferred_study_hour is None:
                profile.preferred_study_hour = hour
            else:
                profile.preferred_study_hour = round(
                    self._ALPHA * hour
                    + (1 - self._ALPHA) * profile.preferred_study_hour
                )
        elif completed_task.category == TaskCategory.HEALTH:
            if profile.preferred_workout_hour is None:
                profile.preferred_workout_hour = hour
            else:
                profile.preferred_workout_hour = round(
                    self._ALPHA * hour
                    + (1 - self._ALPHA) * profile.preferred_workout_hour
                )

        # Average delay
        if delay_minutes is not None:
            profile.avg_delay_minutes = round(
                self._ALPHA * delay_minutes
                + (1 - self._ALPHA) * profile.avg_delay_minutes
            )

        # Focus session length
        if completed_task.duration:
            profile.focus_session_minutes = round(
                self._ALPHA * completed_task.duration
                + (1 - self._ALPHA) * profile.focus_session_minutes
            )

        profile.last_updated = now
        await self.db.flush()
        return profile

    async def record_skip(self, user_id: UUID) -> None:
        """Update completion rate toward 0.0 on task skip."""
        profile = await self.get_profile(user_id)
        profile.completion_rate = (
            self._ALPHA * 0.0 + (1 - self._ALPHA) * profile.completion_rate
        )
        await self.db.flush()

    async def get_suggestions(self, user_id: UUID) -> list[str]:
        """Generate proactive scheduling suggestions based on habit profile."""
        profile = await self.get_profile(user_id)
        suggestions: list[str] = []

        if profile.total_completions < 5:
            suggestions.append(
                "Complete a few more tasks so I can learn your habits and give better suggestions!"
            )
            return suggestions

        if profile.completion_rate < 0.5:
            suggestions.append(
                "Your completion rate is below 50%. Try scheduling fewer tasks per day for a more achievable plan."
            )
        elif profile.completion_rate >= 0.85:
            suggestions.append(
                "Great consistency! You're completing most of your tasks. Consider adding a stretch goal."
            )

        if profile.preferred_study_hour is not None:
            suggestions.append(
                f"You tend to study best around {profile.preferred_study_hour:02d}:00. "
                "Lock this in as a fixed study block?"
            )

        if profile.preferred_workout_hour is not None:
            suggestions.append(
                f"Your workout sessions usually start around {profile.preferred_workout_hour:02d}:00. "
                "Make this a recurring reminder?"
            )

        if profile.avg_delay_minutes > 20:
            suggestions.append(
                f"You typically start tasks about {profile.avg_delay_minutes} minutes late. "
                "Try scheduling a 20-minute buffer after each task."
            )

        if profile.focus_session_minutes > 90:
            suggestions.append(
                f"Your average focus session is {profile.focus_session_minutes} minutes — great deep work! "
                "Add short breaks between sessions to stay sharp."
            )

        return suggestions[:5]  # Return at most 5 suggestions
