from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Routine
from app.repositories.base import BaseRepository


class RoutineRepository(BaseRepository[Routine]):
    def __init__(self, db: AsyncSession):
        super().__init__(Routine, db)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[Routine]:
        query = select(Routine).where(Routine.user_id == user_id)
        if active_only:
            query = query.where(Routine.is_active.is_(True))
        query = query.order_by(Routine.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self, routine_id: UUID, user_id: UUID
    ) -> Routine | None:
        result = await self.db.execute(
            select(Routine).where(
                and_(Routine.id == routine_id, Routine.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: UUID, active_only: bool = False) -> int:
        query = (
            select(func.count()).select_from(Routine).where(Routine.user_id == user_id)
        )
        if active_only:
            query = query.where(Routine.is_active.is_(True))
        result = await self.db.execute(query)
        return result.scalar_one()
