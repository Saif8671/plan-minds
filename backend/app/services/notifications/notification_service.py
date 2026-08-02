from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Notification, NotificationType
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationResponse


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.notification_repo = NotificationRepository(db)

    async def create_notification(
        self,
        user_id: UUID,
        title: str,
        message: str | None = None,
        notification_type: NotificationType = NotificationType.SYSTEM,
        data: dict[str, Any] | None = None,
    ) -> NotificationResponse:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data,
        )
        notification = await self.notification_repo.create(notification)
        return NotificationResponse.model_validate(notification)

    async def get_notifications(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
    ) -> list[NotificationResponse]:
        notifications = await self.notification_repo.get_by_user(
            user_id, skip, limit, unread_only
        )
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def get_unread_count(self, user_id: UUID) -> int:
        return await self.notification_repo.count_unread(user_id)

    async def mark_as_read(
        self, user_id: UUID, notification_id: UUID
    ) -> NotificationResponse:
        notification = await self.notification_repo.get_by_id_and_user(
            notification_id, user_id
        )
        if not notification:
            raise NotFoundError("Notification")
        notification.is_read = True
        notification = await self.notification_repo.update(notification)
        return NotificationResponse.model_validate(notification)

    async def mark_all_as_read(self, user_id: UUID) -> None:
        await self.notification_repo.mark_all_read(user_id)

    async def delete_notification(self, user_id: UUID, notification_id: UUID) -> None:
        notification = await self.notification_repo.get_by_id_and_user(
            notification_id, user_id
        )
        if not notification:
            raise NotFoundError("Notification")
        await self.notification_repo.delete(notification)
