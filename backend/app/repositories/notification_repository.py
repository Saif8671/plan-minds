from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
    ) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read.is_(False))
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self, notification_id: UUID, user_id: UUID
    ) -> Notification | None:
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id, Notification.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def count_unread(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(
                and_(Notification.user_id == user_id, Notification.is_read.is_(False))
            )
        )
        return result.scalar_one()

    async def mark_all_read(self, user_id: UUID) -> None:
        await self.db.execute(
            update(Notification)
            .where(
                and_(Notification.user_id == user_id, Notification.is_read.is_(False))
            )
            .values(is_read=True)
        )
        await self.db.flush()
