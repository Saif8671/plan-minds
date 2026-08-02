from datetime import date
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Schedule, ScheduleStatus
from app.repositories.base import BaseRepository


class ScheduleRepository(BaseRepository[Schedule]):
    def __init__(self, db: AsyncSession):
        super().__init__(Schedule, db)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: ScheduleStatus | None = None,
    ) -> list[Schedule]:
        query = select(Schedule).where(Schedule.user_id == user_id)
        if status:
            query = query.where(Schedule.status == status)
        query = query.order_by(Schedule.start_time.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self, schedule_id: UUID, user_id: UUID
    ) -> Schedule | None:
        result = await self.db.execute(
            select(Schedule).where(
                and_(Schedule.id == schedule_id, Schedule.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def count_by_user(
        self, user_id: UUID, status: ScheduleStatus | None = None
    ) -> int:
        query = (
            select(func.count())
            .select_from(Schedule)
            .where(Schedule.user_id == user_id)
        )
        if status:
            query = query.where(Schedule.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_by_user_and_date(
        self, user_id: UUID, target_date: date
    ) -> Schedule | None:
        result = await self.db.execute(
            select(Schedule).where(
                and_(Schedule.user_id == user_id, Schedule.date == target_date)
            )
        )
        return result.scalar_one_or_none()

    async def get_week_for_user(
        self, user_id: UUID, start_date: date, end_date: date
    ) -> list[Schedule]:
        result = await self.db.execute(
            select(Schedule)
            .where(
                and_(
                    Schedule.user_id == user_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date,
                )
            )
            .order_by(Schedule.date)
        )
        return list(result.scalars().all())
