from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reminder
from app.repositories.base import BaseRepository


class ReminderRepository(BaseRepository[Reminder]):
    def __init__(self, db: AsyncSession):
        super().__init__(Reminder, db)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_sent: bool = True,
    ) -> list[Reminder]:
        query = select(Reminder).where(Reminder.user_id == user_id)
        if not include_sent:
            query = query.where(Reminder.is_sent.is_(False))
        query = query.order_by(Reminder.reminder_time).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self, reminder_id: UUID, user_id: UUID
    ) -> Reminder | None:
        result = await self.db.execute(
            select(Reminder).where(
                and_(Reminder.id == reminder_id, Reminder.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_pending_before(self, before: datetime) -> list[Reminder]:
        result = await self.db.execute(
            select(Reminder).where(
                and_(Reminder.is_sent.is_(False), Reminder.reminder_time <= before)
            )
        )
        return list(result.scalars().all())
