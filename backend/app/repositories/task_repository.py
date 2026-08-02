from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskStatus
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: TaskStatus | None = None,
    ) -> list[Task]:
        query = select(Task).where(Task.user_id == user_id)
        if status:
            query = query.where(Task.status == status)
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(self, task_id: UUID, user_id: UUID) -> Task | None:
        result = await self.db.execute(
            select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def count_by_user(
        self, user_id: UUID, status: TaskStatus | None = None
    ) -> int:
        from sqlalchemy import func

        query = select(func.count()).select_from(Task).where(Task.user_id == user_id)
        if status:
            query = query.where(Task.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_pending_for_user(self, user_id: UUID) -> list[Task]:
        result = await self.db.execute(
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
            )
            .order_by(Task.priority.desc(), Task.deadline.asc().nullslast())
        )
        return list(result.scalars().all())
