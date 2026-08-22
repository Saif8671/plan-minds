"""Gamification service — XP awards, level calculation, streak tracking.

Important: this service does NOT call db.commit() — the transaction is owned
by the caller (request handler via get_db()). This ensures XP is only
permanently awarded if the entire request succeeds.
"""

import math
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskOccurrence, TaskPriority, TaskStatus, User, UserStats


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
                if stats.streak_days > stats.longest_streak:
                    stats.longest_streak = stats.streak_days
            elif stats.last_active_date < today - timedelta(days=1):
                stats.streak_days = 1  # Streak broken
        else:
            stats.streak_days = 1
            if stats.streak_days > stats.longest_streak:
                stats.longest_streak = stats.streak_days

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

    async def get_today_progress(self, user_id: UUID) -> int:
        today = date.today()
        stmt = select(func.count(TaskOccurrence.id)).where(
            TaskOccurrence.user_id == user_id, TaskOccurrence.date == today
        )
        total_stmt = await self.db.execute(stmt)
        total_tasks = total_stmt.scalar() or 0

        if total_tasks == 0:
            return 0

        completed_stmt = select(func.count(TaskOccurrence.id)).where(
            TaskOccurrence.user_id == user_id,
            TaskOccurrence.date == today,
            TaskOccurrence.status == TaskStatus.COMPLETED,
        )
        completed_result = await self.db.execute(completed_stmt)
        completed_tasks = completed_result.scalar() or 0

        return int((completed_tasks / total_tasks) * 100)

    async def get_productivity_score(self, user_id: UUID) -> int:
        today = date.today()
        week_ago = today - timedelta(days=7)

        stmt = select(
            func.count(TaskOccurrence.id).label("total"),
            func.sum(
                case((TaskOccurrence.status == TaskStatus.COMPLETED, 1), else_=0)
            ).label("completed"),
        ).where(
            TaskOccurrence.user_id == user_id,
            TaskOccurrence.date >= week_ago,
            TaskOccurrence.date <= today,
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row or not row.total or row.total == 0:
            return 0
        return int((row.completed / row.total) * 100)

    async def get_badges(self, stats: UserStats) -> list[dict]:
        badges = []
        if stats.level >= 5:
            badges.append(
                {
                    "id": "level_5",
                    "name": "Level 5 Achiever",
                    "icon": "star",
                    "description": "Reached Level 5",
                }
            )
        if stats.streak_days >= 7:
            badges.append(
                {
                    "id": "streak_7",
                    "name": "7-Day Streak",
                    "icon": "flame",
                    "description": "Maintained a 7-day streak",
                }
            )
        if stats.longest_streak >= 30:
            badges.append(
                {
                    "id": "streak_30",
                    "name": "30-Day Streak",
                    "icon": "trophy",
                    "description": "Maintained a 30-day streak",
                }
            )
        return badges
