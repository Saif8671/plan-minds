"""Gamification service — XP awards, level calculation, streak tracking.

Important: this service does NOT call db.commit() — the transaction is owned
by the caller (request handler via get_db()). This ensures XP is only
permanently awarded if the entire request succeeds.
"""

import math
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskPriority, User, UserStats


class GamificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_stats(self, user_id: UUID) -> UserStats:
        stmt = select(UserStats).where(UserStats.user_id == user_id)
        result = await self.db.execute(stmt)
        stats = result.scalar_one_or_none()

        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)
            await self.db.flush()
            await self.db.refresh(stats)

        return stats

    async def get_leaderboard(self, limit: int = 10) -> list[dict]:
        stmt = (
            select(UserStats, User)
            .join(User, UserStats.user_id == User.id)
            .order_by(UserStats.xp.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "user_id": str(user.id),
                "name": user.name or user.email.split("@")[0],
                "level": stats.level,
                "xp": stats.xp,
                "streak_days": stats.streak_days,
            }
            for stats, user in rows
        ]

    def calculate_task_xp(self, task: Task) -> int:
        """Base XP is 1 XP/minute (capped at 120 min), multiplied by priority."""
        duration = min(task.duration or 30, 120)
        priority_multiplier = {
            TaskPriority.LOW: 1.0,
            TaskPriority.MEDIUM: 1.2,
            TaskPriority.HIGH: 1.5,
            TaskPriority.URGENT: 2.0,
        }.get(task.priority, 1.0)
        return int(duration * priority_multiplier)

    def calculate_level(self, xp: int) -> int:
        """Level = int(sqrt(XP / 100)) + 1.

        Examples: 0 XP → L1, 100 XP → L2, 400 XP → L3.
        """
        if xp < 0:
            return 1
        return int(math.sqrt(xp / 100)) + 1

    async def award_task_completion_xp(self, user_id: UUID, task: Task) -> dict:
        """Award XP for completing a task and update streak.

        Does NOT commit — the caller owns the transaction.
        """
        stats = await self.get_user_stats(user_id)
        today = date.today()

        # Streak logic
        if stats.last_active_date:
            if stats.last_active_date == today - timedelta(days=1):
                stats.streak_days += 1
            elif stats.last_active_date < today - timedelta(days=1):
                stats.streak_days = 1  # Streak broken
        else:
            stats.streak_days = 1

        stats.last_active_date = today

        # Streak multiplier: up to 1.5× for 10+ day streak
        streak_multiplier = min(1.0 + (stats.streak_days * 0.05), 1.5)

        base_xp = self.calculate_task_xp(task)
        awarded_xp = int(base_xp * streak_multiplier)

        old_level = stats.level
        stats.xp += awarded_xp
        stats.level = self.calculate_level(stats.xp)
        leveled_up = stats.level > old_level

        # Flush changes into the session without committing
        await self.db.flush()
        await self.db.refresh(stats)

        return {
            "awarded_xp": awarded_xp,
            "new_total_xp": stats.xp,
            "streak_days": stats.streak_days,
            "leveled_up": leveled_up,
            "current_level": stats.level,
        }
