from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityLog, Task
from app.repositories.base import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(ActivityLog, db)

    async def get_by_user_tasks(
        self, user_id: UUID, skip: int = 0, limit: int = 500
    ) -> list[ActivityLog]:
        result = await self.db.execute(
            select(ActivityLog)
            .join(Task, ActivityLog.task_id == Task.id)
            .where(Task.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
