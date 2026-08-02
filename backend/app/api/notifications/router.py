from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import MessageResponse
from app.schemas.notification import NotificationResponse
from app.services.notifications.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    current_user: CurrentUser,
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = False,
):
    service = NotificationService(db)
    return await service.get_notifications(current_user.id, skip, limit, unread_only)


@router.get("/unread-count")
async def get_unread_count(current_user: CurrentUser, db: DbSession):
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = NotificationService(db)
    return await service.mark_as_read(current_user.id, notification_id)


@router.post("/read-all", response_model=MessageResponse)
async def mark_all_as_read(current_user: CurrentUser, db: DbSession):
    service = NotificationService(db)
    await service.mark_all_as_read(current_user.id)
    return MessageResponse(message="All notifications marked as read")


@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = NotificationService(db)
    await service.delete_notification(current_user.id, notification_id)
