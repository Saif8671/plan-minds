from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.notification import PushSubscriptionCreate, PushSubscriptionResponse
from app.services.notifications.push_service import PushService

router = APIRouter(prefix="/notifications/push", tags=["Push Notifications"])


@router.post("/subscribe", response_model=PushSubscriptionResponse)
async def subscribe(
    data: PushSubscriptionCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = PushService(db)
    sub = await service.subscribe(
        user_id=current_user.id,
        endpoint=data.endpoint,
        p256dh=data.p256dh,
        auth=data.auth,
    )
    return sub


@router.delete("/unsubscribe", status_code=204)
async def unsubscribe(
    endpoint: str,
    current_user: CurrentUser,
    db: DbSession,
):
    service = PushService(db)
    await service.unsubscribe(current_user.id, endpoint)
